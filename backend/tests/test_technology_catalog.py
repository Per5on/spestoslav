from pathlib import Path
import importlib.util
import pytest
from sqlalchemy import select, func
import test_locality_search as fixture
from app.main import app
from app.db import get_db
from app.models import Product, Retailer
from app.technology import TechnologyIdentity
from app.marketplace import CurrentPrice, ProductBarcode

spec = importlib.util.spec_from_file_location(
    "technology_import_test",
    Path(__file__).resolve().parents[2] / "scripts/import_technology_catalog.py",
)
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


@pytest.fixture(autouse=True)
def database(monkeypatch):
    fixture.setup_function()
    app.dependency_overrides[get_db] = fixture.override_get_db
    monkeypatch.setenv("ENABLE_DEMO_CATALOG", "true")
    yield
    fixture.teardown_function()


def test_technology_1000_idempotent_provenance_and_snapshot():
    data = importer.load_catalog()
    with fixture.TestingSessionLocal.begin() as db:
        assert importer.import_catalog(db, data) == 1000
        target = db.scalar(select(Product).where(Product.category_code == "technology"))
        identity = target.id
        assert db.get(Retailer, "techmart").website_url == "https://techmart.bg/"
        db.get(Retailer, "techmart").active = False
        target.barcode = "4006381333931"
        target.active = False
    with fixture.TestingSessionLocal.begin() as db:
        importer.import_catalog(db, data)
        assert db.scalar(select(func.count()).select_from(TechnologyIdentity)) == 1000
        assert db.get(Product, identity).barcode == "4006381333931"
        assert not db.get(Product, identity).active
        assert not db.get(Retailer, "techmart").active
        assert (
            db.scalar(select(func.count()).select_from(ProductBarcode)) == 1
        )  # pre-existing synthetic fixture only
        assert db.scalar(select(func.count()).select_from(CurrentPrice)) == 1
    result = fixture.client.get("/api/v1/catalog/technology")
    assert (
        result.status_code == 200
        and result.headers["cache-control"] == "public, max-age=300"
    )
    rows = result.json()["products"]
    assert len(rows) == 999
    assert all(
        p["category_code"] == "technology"
        and p["source_url"].startswith("https://techmart.bg/")
        for p in rows
    )
    assert all("price_eur" not in p and p["barcode"] is None for p in rows)


def test_sample_thumbnails_are_local_credited_and_separate_from_prices():
    groceries = fixture.client.get("/api/v1/demo/catalog").json()
    technology = fixture.client.get(
        "/api/v1/demo/catalog?category_code=technology"
    ).json()
    assert len(groceries["products"]) == 3 and len(technology["products"]) == 6
    for row in groceries["products"] + technology["products"]:
        assert row["is_demo"] and row["price_eur"] is None and not row["verified"]
        image = fixture.client.get(row["image_url"])
        assert image.status_code == 200 and image.headers["content-type"].startswith(
            "image/"
        )
    credits = fixture.client.get("/api/v1/demo/credits").json()
    assert len(credits) == 9
    assert all(r["license"] and r["author"] for r in credits)
    assert fixture.client.get("/api/v1/demo/images/not-an-asset").status_code == 404
