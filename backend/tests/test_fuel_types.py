"""Fuel selector metadata must not create price/stock claims or reactivate history."""

import importlib.util
import json
from pathlib import Path

import pytest
import test_locality_search as fixture
from app.db import get_db
from app.main import app
from app.marketplace import CurrentPrice
from app.models import Product
from sqlalchemy import func, select

spec = importlib.util.spec_from_file_location(
    "fuel_import", Path(__file__).resolve().parents[2] / "scripts/import_fuel_types.py"
)
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


@pytest.fixture(autouse=True)
def database():
    fixture.setup_function()
    app.dependency_overrides[get_db] = fixture.override_get_db
    yield
    fixture.teardown_function()


def test_five_approved_fuel_grades_available_without_invented_prices():
    with fixture.TestingSessionLocal.begin() as db:
        before = db.scalar(select(func.count()).select_from(CurrentPrice))
        assert importer.import_types(db, importer.load_types()) == 5
        assert db.scalar(select(func.count()).select_from(CurrentPrice)) == before
    rows = fixture.client.get("/api/v1/products?category_code=fuel").json()
    assert len(rows) == 5
    assert {r["fuel_type"] for r in rows} == importer.CODES
    assert all(r["barcode"] is None for r in rows)


def test_repeat_retains_inactive_and_barcode():
    rows = importer.load_types()
    identity = importer.product_id("petrol")
    with fixture.TestingSessionLocal.begin() as db:
        importer.import_types(db, rows)
        db.get(Product, identity).active = False
        db.get(Product, identity).barcode = "12345670"
    with fixture.TestingSessionLocal.begin() as db:
        importer.import_types(db, rows)
        assert (
            db.scalar(
                select(func.count())
                .select_from(Product)
                .where(Product.category_code == "fuel")
            )
            == 5
        )
        assert db.get(Product, identity).active is False
        assert db.get(Product, identity).barcode == "12345670"


def test_existing_identity_conflict_requires_review():
    with fixture.TestingSessionLocal.begin() as db:
        db.add(
            Product(
                id=importer.product_id("petrol"),
                category_code="groceries",
                name="Synthetic conflict",
                normalized_name="synthetic conflict",
            )
        )
    with (
        pytest.raises(ValueError, match="identity conflict"),
        fixture.TestingSessionLocal.begin() as db,
    ):
        importer.import_types(db, importer.load_types())
    with fixture.TestingSessionLocal() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(Product)
                .where(Product.category_code == "fuel")
            )
            == 0
        )


def test_unverified_values_cannot_be_added_to_taxonomy(tmp_path):
    data = json.loads(importer.PATH.read_text())
    data["products"][0]["price_eur"] = 1
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="No inferred"):
        importer.load_types(path)


def test_fuel_snapshot_agrees_with_old_routes_and_hides_nonfuel_inventory():
    with fixture.TestingSessionLocal.begin() as db:
        importer.import_types(db, importer.load_types())
    locality = fixture.client.get("/api/v1/localities?q=Sofija").json()[0]["id"]
    query = f"category_code=fuel&locality_id={locality}"
    response = fixture.client.get(f"/api/v1/fuel-snapshot?locality_id={locality}")
    assert response.status_code == 200
    result = response.json()
    assert result["schema_version"] == 1
    assert result["locality_id"] == locality
    assert set(p["fuel_type"] for p in result["products"]) == importer.CODES
    for key, route in (("stores", "stores"), ("prices", "prices/current"), ("online", "national-offers")):
        assert result[key] == fixture.client.get(f"/api/v1/{route}?{query}").json() == []
    assert fixture.client.get("/api/v1/fuel-snapshot?locality_id=not-a-uuid").status_code == 422
