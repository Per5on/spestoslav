"""Regression coverage for live-schema compatibility, readiness and offer visibility."""

from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import update

import test_locality_search as fixtures
from app.db import get_db, normalize_database_url
from app.main import app
from app.models import Category, Product, Retailer, StoreBranch
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
        db.exec_driver_sql("DROP TABLE product_images")
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


def test_name_search_has_no_postal_storage_dependency():
    from sqlalchemy import inspect

    inspector = inspect(fixtures.engine)
    assert "locality_postal_codes" not in inspector.get_table_names()
    assert "postal_code" not in {
        c["name"] for c in inspector.get_columns("inhabited_localities")
    }
    assert "postal_code" not in {
        c["name"] for c in inspector.get_columns("store_branches")
    }
    response = fixtures.client.get("/api/v1/localities", params={"q": "Sofia"})
    assert response.status_code == 200
    assert response.json()[0]["name_bg"] == "София"
    assert response.json()[0]["postal_codes"] == []
