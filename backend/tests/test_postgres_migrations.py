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
        # Two open transactions must be able to claim different queued receipts.
        # A SELECT without LIMIT locks every eligible row before .first() runs.
        from app.marketplace import ReceiptScan
        from app.workflows import ReceiptJob
        from app.receipt_processing import claim_job

        with sessions.begin() as db:
            for number in range(2):
                scan = ReceiptScan(
                    image_storage_key=f"test/receipt-{number}.png", status="UPLOADED"
                )
                db.add(scan)
                db.flush()
                db.add(ReceiptJob(scan_id=scan.id, owner_subject="postgres-test-user"))
        with sessions() as first, sessions() as second:
            first.execute(text("SET LOCAL statement_timeout = '5s'"))
            second.execute(text("SET LOCAL statement_timeout = '5s'"))
            one = claim_job(first)
            two = claim_job(second)
            assert one is not None and two is not None
            assert one[0].id != two[0].id
            first.rollback()
            second.rollback()

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


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"), reason="Requires disposable PostgreSQL"
)
def test_grocery_orm_and_connected_sql_imports_keep_identical_ids(monkeypatch):
    import importlib.util
    from sqlalchemy.orm import sessionmaker
    from app.grocery import GroceryIdentity
    from app.models import Product

    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "grocery_import_pg", root.parent / "scripts/import_grocery_catalog.py"
    )
    importer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(importer)
    engine = create_engine(normalize_database_url(os.environ["TEST_DATABASE_URL"]))
    schema = "grocery_" + uuid.uuid4().hex
    with engine.begin() as db:
        db.execute(text(f'CREATE SCHEMA "{schema}"'))
    scoped = make_url(engine.url).update_query_dict(
        {"options": f"-csearch_path={schema}"}
    )
    scoped_engine = create_engine(scoped)
    sessions = sessionmaker(bind=scoped_engine)
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    monkeypatch.setenv("DATABASE_URL", scoped.render_as_string(hide_password=False))
    try:
        command.upgrade(config, "head")
        data = importer.load_catalog()
        with sessions.begin() as db:
            importer.import_catalog(db, data)
        with sessions.begin() as db:
            first = sorted(
                str(x)
                for x in db.scalars(
                    __import__("sqlalchemy").select(GroceryIdentity.product_id)
                )
            )
            product = db.get(Product, uuid.UUID(first[0]))
            product.barcode = "4006381333931"
        with scoped_engine.begin() as db:
            for sql in importer.catalog_sql(data):
                db.execute(text(sql))
        with sessions.begin() as db:
            importer.import_catalog(db, data)
            second = sorted(
                str(x)
                for x in db.scalars(
                    __import__("sqlalchemy").select(GroceryIdentity.product_id)
                )
            )
            assert len(first) == 1000 and first == second
            assert db.get(Product, uuid.UUID(first[0])).barcode == "4006381333931"
        command.check(config)
    finally:
        scoped_engine.dispose()
        with engine.begin() as db:
            db.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        engine.dispose()


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"), reason="Requires disposable PostgreSQL"
)
def test_whole_sql_file_preserves_quoted_semicolons_and_dollar_bodies(
    tmp_path, monkeypatch
):
    from io import StringIO
    from alembic.migration import MigrationContext
    from migrations import sql_file

    engine = create_engine(normalize_database_url(os.environ["TEST_DATABASE_URL"]))
    schema = "sqlfile_" + uuid.uuid4().hex
    path = tmp_path / "literal.sql"
    path.write_text(
        "CREATE TABLE literal_test (value TEXT);\nINSERT INTO literal_test VALUES ('a;b :named');\nDO $$ BEGIN PERFORM 1; END $$;\n"
    )
    with engine.begin() as db:
        db.execute(text(f'CREATE SCHEMA "{schema}"'))
    try:
        with engine.begin() as db:
            db.execute(text(f'SET LOCAL search_path="{schema}"'))
            online = MigrationContext.configure(db)
            monkeypatch.setattr(sql_file.op, "get_context", lambda: online)
            monkeypatch.setattr(sql_file.op, "get_bind", lambda: db)
            sql_file.execute_sql_file(path)
            assert db.scalar(text("SELECT value FROM literal_test")) == "a;b :named"
        output = StringIO()
        offline = MigrationContext.configure(
            url="postgresql+psycopg://", opts={"as_sql": True, "output_buffer": output}
        )
        monkeypatch.setattr(sql_file.op, "get_context", lambda: offline)
        sql_file.execute_sql_file(path)
        assert (
            "'a;b :named'" in output.getvalue()
            and "DO $$ BEGIN PERFORM 1; END $$;" in output.getvalue()
        )
        assert "NULL" not in output.getvalue()
    finally:
        with engine.begin() as db:
            db.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        engine.dispose()
