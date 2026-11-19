"""Endpoint-level barcode lookup regressions: verified identity, not scan success."""

import uuid

import pytest
from sqlalchemy import update

import test_locality_search as fixtures
from app.db import get_db
from app.main import app
from app.marketplace import ProductBarcode
from app.models import Category, Product


@pytest.fixture(autouse=True)
def database():
    previous = dict(app.dependency_overrides)
    fixtures.setup_function()
    app.dependency_overrides[get_db] = fixtures.override_get_db
    yield
    fixtures.teardown_function()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


def test_barcode_lookup_distinguishes_invalid_unknown_and_verified():
    client = fixtures.client
    assert client.get("/api/v1/products/barcode/4006381333932").status_code == 422
    assert client.get("/api/v1/products/barcode/4006381333931").status_code == 404
    found = client.get("/api/v1/products/barcode/3800000000003")
    assert found.status_code == 200
    assert found.json()["barcodes"] == ["3800000000003"]


def test_unverified_secondary_barcode_is_not_a_product_match_or_exposed():
    with fixtures.TestingSessionLocal() as db:
        product = db.query(Product).first()
        db.add(ProductBarcode(
            product_id=product.id, barcode="4006381333931",
            source="TEST", verified=False,
        ))
        db.commit()
    assert fixtures.client.get("/api/v1/products/barcode/4006381333931").status_code == 404
    response = fixtures.client.get("/api/v1/products/barcode/3800000000003")
    assert response.status_code == 200
    assert response.json()["barcodes"] == ["3800000000003"]


def test_verified_secondary_barcode_matches_product_and_zero_padded_alias():
    with fixtures.TestingSessionLocal() as db:
        product = db.query(Product).first()
        db.add(ProductBarcode(
            product_id=product.id, barcode="036000291452",
            source="TEST", verified=True,
        ))
        db.commit()
    for code in ("036000291452", "0036000291452", "00036000291452"):
        response = fixtures.client.get(f"/api/v1/products/barcode/{code}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test product"
        assert "036000291452" in response.json()["barcodes"]


def test_barcode_collision_between_products_requires_review():
    with fixtures.TestingSessionLocal() as db:
        db.add(Product(
            id=uuid.uuid4(), category_code="FOOD", name="Second",
            normalized_name="second", barcode="4006381333931",
        ))
        db.flush()
        first = db.query(Product).filter(Product.name == "Test product").one()
        db.add(ProductBarcode(
            product_id=first.id, barcode="04006381333931",
            source="TEST", verified=True,
        ))
        db.commit()
    assert fixtures.client.get("/api/v1/products/barcode/4006381333931").status_code == 409


def test_inactive_product_or_category_is_not_returned():
    with fixtures.TestingSessionLocal() as db:
        db.execute(update(Product).values(active=False))
        db.commit()
    assert fixtures.client.get("/api/v1/products/barcode/3800000000003").status_code == 404
    with fixtures.TestingSessionLocal() as db:
        db.execute(update(Product).values(active=True))
        db.execute(update(Category).values(active=False))
        db.commit()
    assert fixtures.client.get("/api/v1/products/barcode/3800000000003").status_code == 404
