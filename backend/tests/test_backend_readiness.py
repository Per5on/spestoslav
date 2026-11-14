"""Regression coverage for live-schema compatibility, readiness and offer visibility."""

from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import select, update
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import load_only
from fastapi.testclient import TestClient

import test_locality_search as fixtures
from app.db import get_db, normalize_database_url
from app.main import app
from app.models import Category, Product, Retailer, StoreBranch, Locality
from app.marketplace import CurrentPrice, Promotion


@pytest.fixture(autouse=True)
def database():
    previous = dict(app.dependency_overrides)
    fixtures.setup_function()
    app.dependency_overrides[get_db] = fixtures.override_get_db
    yield
    fixtures.teardown_function()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


@pytest.mark.parametrize("model", [Category, Product, Retailer, StoreBranch])
def test_inactive_entities_hide_all_offers(model):
    with fixtures.TestingSessionLocal() as db:
        db.execute(update(model).values(active=False))
        db.commit()
    assert fixtures.client.get("/api/v1/prices/current").json() == []
    assert fixtures.client.get("/api/v1/promotions").json() == []


def test_expired_unverified_and_future_offers_hidden():
    with fixtures.TestingSessionLocal() as db:
        db.execute(
            update(CurrentPrice).values(
                verified_at=datetime.now(timezone.utc) + timedelta(days=1)
            )
        )
        db.execute(update(Promotion).values(verified=False))
        db.commit()
    assert fixtures.client.get("/api/v1/prices/current").json() == []
    assert fixtures.client.get("/api/v1/promotions").json() == []
    with fixtures.TestingSessionLocal() as db:
        db.execute(
            update(CurrentPrice).values(
                verified_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            )
        )
        db.commit()
    assert fixtures.client.get("/api/v1/prices/current").json() == []


def test_ready_checks_database_and_health_is_liveness():
    assert fixtures.client.get("/ready").status_code == 200
    # Simulate a database whose migration/normalization is missing.
    with fixtures.engine.begin() as db:
        db.exec_driver_sql("DROP TABLE locality_postal_codes")
    response = fixtures.client.get("/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == "Database is not ready"
    assert fixtures.client.get("/health").status_code == 200


@pytest.mark.parametrize(
    "url",
    [
        "postgres://u:p@host/db?sslmode=require",
        "postgresql://u:p@host/db?sslmode=require",
        "postgresql+psycopg://u:p@host/db?sslmode=require",
    ],
)
def test_postgres_driver_is_explicit(url):
    assert (
        normalize_database_url(url)
        == "postgresql+psycopg://u:p@host/db?sslmode=require"
    )


def test_locality_search_works_without_legacy_postal_column():
    # Exactly the live-preview failure: normalized postal table exists but the
    # old single-postal column does not. Do not fix it by changing Flyway tables.
    with fixtures.engine.begin() as db:
        db.exec_driver_sql("DROP INDEX ix_localities_postal_code")
        db.exec_driver_sql("ALTER TABLE inhabited_localities DROP COLUMN postal_code")
    response = fixtures.client.get("/api/v1/localities", params={"q": "Sofia"})
    assert response.status_code == 200
    assert response.json()[0]["postal_codes"] == ["1000"]
