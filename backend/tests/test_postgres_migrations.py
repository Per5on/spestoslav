"""Run actual migrations in a disposable PostgreSQL schema (never public)."""

import os
import uuid
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from app.db import normalize_database_url


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL requires a disposable PostgreSQL instance",
)
def test_migrations_round_trip_match_models_and_offline_sql(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    url = normalize_database_url(os.environ["TEST_DATABASE_URL"])
    engine = create_engine(url)
    schema = "audit_" + uuid.uuid4().hex
    with engine.begin() as db:
        db.execute(text(f'CREATE SCHEMA "{schema}"'))
    scoped = make_url(url).update_query_dict({"options": f"-csearch_path={schema}"})
    monkeypatch.setenv("DATABASE_URL", scoped.render_as_string(hide_password=False))
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    try:
        command.upgrade(config, "head")
        command.check(config)
        command.downgrade(config, "base")
        command.upgrade(config, "head")
        command.check(config)
        # Exercise the real PostgreSQL transaction/upsert path after migrations.
        from sqlalchemy.orm import sessionmaker
        from fastapi.testclient import TestClient
        from app.main import app
        from app.db import get_db
        from app.auth import Principal, current_user
        from app.models import Category, Locality, Retailer, Product, StoreBranch
        from app.marketplace import CurrentPrice
        from datetime import datetime, timedelta, timezone

        scoped_engine = create_engine(scoped)
        sessions = sessionmaker(bind=scoped_engine, expire_on_commit=False)
        with sessions.begin() as db:
            category = Category(code="fuel", name_bg="Горива", name_en="Fuel")
            locality = Locality(
                source="TEST",
                source_id="pg-sofia",
                name="Sofija",
                name_bg="София",
                name_latin="Sofija",
                municipality="Столична",
                region="София (столица)",
            )
            db.add_all([category, locality])
            db.flush()
            retailer = Retailer(
                code="PG_TEST", name="Postgres test", category_code="fuel"
            )
            product = Product(
                category_code="fuel", name="Test diesel", normalized_name="test diesel"
            )
            db.add_all([retailer, product])
            db.flush()
            branch = StoreBranch(
                retailer_code=retailer.code,
                locality_id=locality.id,
                address="Test street 1",
            )
            db.add(branch)
            db.flush()
            product_id = product.id
            branch_id = branch.id
        previous = dict(app.dependency_overrides)

        def database():
            with sessions() as db:
                yield db

        app.dependency_overrides[get_db] = database
        app.dependency_overrides[current_user] = lambda: Principal("postgres-test-user")
        monkeypatch.setenv("ADMIN_API_KEY", "pg-test-" + ("x" * 40))
        try:
            client = TestClient(app)
            assert client.get("/ready").status_code == 200
            payload = {
                "product_id": str(product_id),
                "branch_id": str(branch_id),
                "price_eur": "1.83",
                "source_reference": "https://official.example/evidence",
                "expires_at": (
                    datetime.now(timezone.utc) + timedelta(days=1)
                ).isoformat(),
            }
            submitted = client.post(
                "/api/v1/submissions/prices",
                json=payload,
                headers={"Idempotency-Key": "postgres-request-123"},
            )
            assert submitted.status_code == 201, submitted.text
            assert client.get("/api/v1/prices/current").json() == []
            submission_id = submitted.json()["id"]

            def approve():
                return (
                    TestClient(app)
                    .post(
                        "/api/v1/admin/submissions/" + submission_id + "/review",
                        json={
                            "decision": "APPROVED",
                            "note": "Reviewed PostgreSQL test evidence",
                        },
                        headers={"X-Admin-Key": "pg-test-" + ("x" * 40)},
                    )
                    .status_code
                )

            from concurrent.futures import ThreadPoolExecutor

            with ThreadPoolExecutor(max_workers=2) as executor:
                statuses = sorted(executor.map(lambda _: approve(), range(2)))
            assert statuses == [200, 409]
            assert client.get("/api/v1/prices/current").json()[0]["price_eur"] == 1.83
            with sessions() as db:
                assert (
                    len(db.scalars(__import__("sqlalchemy").select(CurrentPrice)).all())
                    == 1
                )
        finally:
            app.dependency_overrides.clear()
            app.dependency_overrides.update(previous)
            scoped_engine.dispose()
        from io import StringIO

        config.output_buffer = StringIO()
        command.upgrade(config, "head", sql=True)
        assert "CREATE TABLE receipt_items" in config.output_buffer.getvalue()
    finally:
        # Only this random test schema, on the explicitly supplied test database.
        with engine.begin() as db:
            db.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        engine.dispose()
