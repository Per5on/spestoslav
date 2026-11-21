from datetime import datetime, timedelta, timezone
from io import BytesIO
from decimal import Decimal

from PIL import Image
import pytest
from sqlalchemy import select

import test_locality_search as fixtures
from app.main import app
from app.db import get_db
from app.auth import Principal, current_user
from app.marketplace import PriceCache
from app.models import Product, StoreBranch
from app.receipt_worker import process_one


@pytest.fixture(autouse=True)
def database(monkeypatch):
    previous = dict(app.dependency_overrides)
    fixtures.setup_function()
    app.dependency_overrides[get_db] = fixtures.override_get_db
    monkeypatch.setenv("ADMIN_API_KEY", "test-admin-key-" + ("a" * 40))
    monkeypatch.setenv("COLLECTOR_API_KEY", "test-collector-key-" + ("b" * 40))
    yield
    fixtures.teardown_function()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


ADMIN = {"X-Admin-Key": "test-admin-key-" + ("a" * 40)}
COLLECTOR = {"X-Collector-Key": "test-collector-key-" + ("b" * 40)}


def user(subject="alice"):
    app.dependency_overrides[current_user] = lambda: Principal(subject)


def price():
    with fixtures.TestingSessionLocal() as db:
        product = db.scalar(select(Product))
        branch = db.scalar(select(StoreBranch))
        return {
            "product_id": str(product.id),
            "branch_id": str(branch.id),
            "price_eur": "1.3400",
            "source_reference": "https://retailer.example/price-evidence",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        }


def test_mutations_fail_closed_without_credentials():
    assert (
        fixtures.client.post(
            "/api/v1/submissions/prices",
            json=price(),
            headers={"Idempotency-Key": "request-123"},
        ).status_code
        == 401
    )
    assert fixtures.client.post("/api/v1/admin/products", json={}).status_code == 401
    assert (
        fixtures.client.post("/api/v1/collector/observations", json={}).status_code
        == 401
    )


def test_submission_idempotency_ownership_and_approval():
    user()
    payload = price()
    headers = {"Idempotency-Key": "request-123"}
    response = fixtures.client.post(
        "/api/v1/submissions/prices", json=payload, headers=headers
    )
    assert response.status_code == 201, response.text
    submission = response.json()
    assert submission["status"] == "PENDING"
    assert (
        fixtures.client.post(
            "/api/v1/submissions/prices", json=payload, headers=headers
        ).json()["id"]
        == submission["id"]
    )
    assert (
        fixtures.client.post(
            "/api/v1/submissions/prices",
            json=dict(payload, price_eur="2"),
            headers=headers,
        ).status_code
        == 409
    )
    user("bob")
    assert fixtures.client.get("/api/v1/submissions").json() == []
    user("alice")
    # Unreviewed value is not the current published price.
    assert fixtures.client.get("/api/v1/prices/current").json()[0]["price_eur"] == 1.25
    response = fixtures.client.post(
        "/api/v1/admin/submissions/" + submission["id"] + "/review",
        json={"decision": "APPROVED", "note": "Checked source and branch"},
        headers=ADMIN,
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "VERIFIED"
    assert fixtures.client.get("/api/v1/prices/current").json()[0]["price_eur"] == 1.34
    assert (
        fixtures.client.post(
            "/api/v1/admin/submissions/" + submission["id"] + "/review",
            json={"decision": "APPROVED", "note": "Second attempt"},
            headers=ADMIN,
        ).status_code
        == 409
    )


def test_invalid_prices_and_user_cannot_set_verification():
    user()
    payload = price()
    for fields in (
        {"price_eur": "-1"},
        {"price_eur": "NaN"},
        {"verified": True},
        {"expires_at": "2020-01-01T00:00:00Z"},
        {"expires_at": "2026-11-14T12:00:00"},
        {"source": "ADMIN"},
    ):
        response = fixtures.client.post(
            "/api/v1/submissions/prices",
            json=dict(payload, **fields),
            headers={"Idempotency-Key": "invalid-123"},
        )
        assert response.status_code == 422, response.text


def test_rejection_never_publishes():
    user()
    r = fixtures.client.post(
        "/api/v1/submissions/prices",
        json=price(),
        headers={"Idempotency-Key": "reject-123"},
    )
    review = fixtures.client.post(
        "/api/v1/admin/submissions/" + r.json()["id"] + "/review",
        json={"decision": "REJECTED", "note": "Evidence insufficient"},
        headers=ADMIN,
    )
    assert review.json()["status"] == "REJECTED"
    assert fixtures.client.get("/api/v1/prices/current").json()[0]["price_eur"] == 1.25


def test_collector_allowlist_idempotency_and_pending_review():
    payload = price()
    source = {
        "code": "test",
        "retailer_code": "TEST",
        "origin": "https://retailer.example",
        "enabled": True,
    }
    assert (
        fixtures.client.post(
            "/api/v1/admin/collection-sources", json=source, headers=ADMIN
        ).status_code
        == 201
    )
    item = dict(payload, source_code="test", external_id="official-2026-1")
    response = fixtures.client.post(
        "/api/v1/collector/observations",
        json={"observations": [item]},
        headers=COLLECTOR,
    )
    assert response.status_code == 201, response.text
    assert response.json()[0]["status"] == "PENDING"
    again = fixtures.client.post(
        "/api/v1/collector/observations",
        json={"observations": [item]},
        headers=COLLECTOR,
    )
    assert again.json()[0]["id"] == response.json()[0]["id"]
    bad = dict(item, source_reference="https://evil.example/price", external_id="new")
    assert (
        fixtures.client.post(
            "/api/v1/collector/observations",
            json={"observations": [bad]},
            headers=COLLECTOR,
        ).status_code
        == 422
    )
    # All-or-nothing: the valid first item is rolled back when a later one fails.
    first = dict(item, external_id="new-valid")
    assert (
        fixtures.client.post(
            "/api/v1/collector/observations",
            json={"observations": [first, bad]},
            headers=COLLECTOR,
        ).status_code
        == 422
    )
    with fixtures.TestingSessionLocal() as db:
        assert len(db.scalars(select(PriceCache)).all()) == 1


def test_receipt_upload_worker_and_owner_scope(tmp_path, monkeypatch):
    monkeypatch.setenv("RECEIPT_STORAGE_DIR", str(tmp_path))
    user()
    image = BytesIO()
    Image.new("RGB", (20, 20), "white").save(image, format="PNG")
    response = fixtures.client.post(
        "/api/v1/receipts",
        files={"file": ("receipt.png", image.getvalue(), "image/png")},
    )
    assert response.status_code == 202, response.text
    scan_id = response.json()["id"]
    assert (
        process_one(
            fixtures.TestingSessionLocal, ocr=lambda data: "Мляко 1,34\nОБЩО 1,34"
        )
        is True
    )
    result = fixtures.client.get("/api/v1/receipts/" + scan_id)
    assert result.json()["status"] == "NEEDS_REVIEW"
    assert result.json()["items"][0]["status"] == "UNMATCHED"
    assert fixtures.client.get("/api/v1/prices/current").json()[0]["price_eur"] == 1.25
    user("bob")
    assert fixtures.client.get("/api/v1/receipts/" + scan_id).status_code == 404


def test_receipt_validation_and_missing_storage(monkeypatch):
    user()
    assert (
        fixtures.client.post(
            "/api/v1/receipts",
            files={"file": ("bad.png", b"not-an-image", "image/png")},
        ).status_code
        == 422
    )
    image = BytesIO()
    Image.new("RGB", (2, 2)).save(image, format="PNG")
    monkeypatch.delenv("RECEIPT_STORAGE_DIR", raising=False)
    monkeypatch.delenv("RECEIPT_S3_BUCKET", raising=False)
    assert (
        fixtures.client.post(
            "/api/v1/receipts", files={"file": ("r.png", image.getvalue(), "image/png")}
        ).status_code
        == 503
    )


def test_product_catalog_creation_gtin_validation_and_duplicate():
    payload = {
        "category_code": "FOOD",
        "name": "Reviewed test product",
        "barcode": "4006381333931",
    }
    response = fixtures.client.post(
        "/api/v1/admin/products", json=payload, headers=ADMIN
    )
    assert response.status_code == 201, response.text
    assert (
        fixtures.client.get("/api/v1/products", params={"q": "reviewed test"}).json()[
            0
        ]["name"]
        == payload["name"]
    )
    assert (
        fixtures.client.post(
            "/api/v1/admin/products", json=payload, headers=ADMIN
        ).status_code
        == 409
    )
    assert (
        fixtures.client.post(
            "/api/v1/admin/products",
            json=dict(payload, barcode="4006381333932"),
            headers=ADMIN,
        ).status_code
        == 422
    )


def test_fuelo_cannot_be_labeled_official_and_unknown_cannot_be_published():
    source = {
        "code": "fuelo",
        "retailer_code": "TEST",
        "origin": "https://api.fuelo.net",
        "enabled": True,
    }
    assert (
        fixtures.client.post(
            "/api/v1/admin/collection-sources", json=source, headers=ADMIN
        ).status_code
        == 422
    )
    assert (
        fixtures.client.post(
            "/api/v1/admin/collection-sources",
            json=dict(source, kind="AGGREGATOR"),
            headers=ADMIN,
        ).status_code
        == 201
    )
    item = dict(
        price(),
        source_reference="https://api.fuelo.net/v2/gasstations/123/prices",
        source_code="fuelo",
        external_id="station-123-price-1",
    )
    response = fixtures.client.post(
        "/api/v1/collector/observations",
        json={"observations": [item]},
        headers=COLLECTOR,
    )
    assert response.status_code == 201, response.text
    row = response.json()[0]
    assert row["source"] == "AGGREGATOR_UNKNOWN"
    result = fixtures.client.post(
        "/api/v1/admin/submissions/" + row["id"] + "/review",
        json={"decision": "APPROVED", "note": "Only aggregator evidence"},
        headers=ADMIN,
    )
    assert result.status_code == 409
    assert fixtures.client.get("/api/v1/prices/current").json()[0]["price_eur"] == 1.25


def test_receipt_submission_uses_server_provenance_and_review_queue(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("RECEIPT_STORAGE_DIR", str(tmp_path))
    user()
    image = BytesIO()
    Image.new("RGB", (10, 10), "white").save(image, format="PNG")
    response = fixtures.client.post(
        "/api/v1/receipts",
        files={"file": ("receipt.png", image.getvalue(), "image/png")},
    )
    scan_id = response.json()["id"]
    assert process_one(fixtures.TestingSessionLocal, ocr=lambda data: "Milk 1.34")
    result = fixtures.client.get("/api/v1/receipts/" + scan_id).json()
    item_id = result["items"][0]["id"]
    payload = price()
    payload["source_reference"] = "https://attacker.example/forged"
    path = f"/api/v1/receipts/{scan_id}/items/{item_id}/submit-price"
    response = fixtures.client.post(path, json=payload)
    assert response.status_code == 201, response.text
    assert response.json()["source_reference"] == f"receipt:{scan_id}:item:{item_id}"
    assert response.json()["status"] == "PENDING"
    assert (
        fixtures.client.get(
            "/api/v1/admin/receipts/" + scan_id, headers=ADMIN
        ).status_code
        == 200
    )
    user("bob")
    assert fixtures.client.post(path, json=payload).status_code == 404


def test_upload_stream_limit_precedes_multipart_spooling():
    user()
    response = fixtures.client.post(
        "/api/v1/receipts",
        content=b"small",
        headers={"Content-Length": str(10 * 1024 * 1024)},
    )
    assert response.status_code == 413


def test_unknown_barcode_request_is_private_and_admin_resolvable():
    user()
    barcode = "4006381333931"
    assert fixtures.client.get("/api/v1/products/barcode/" + barcode).status_code == 404
    response = fixtures.client.post(
        "/api/v1/product-identification-requests",
        json={"barcode": barcode, "description": "Please identify"},
    )
    assert response.status_code == 201, response.text
    request_id = response.json()["id"]
    user("bob")
    assert fixtures.client.get("/api/v1/product-identification-requests").json() == []
    with fixtures.TestingSessionLocal() as db:
        product_id = str(db.scalar(select(Product.id)))
    response = fixtures.client.post(
        "/api/v1/admin/product-identification-requests/" + request_id + "/resolve",
        json={"product_id": product_id},
        headers=ADMIN,
    )
    assert response.status_code == 200, response.text
    assert (
        fixtures.client.get("/api/v1/products/barcode/" + barcode).json()["id"]
        == product_id
    )


def test_older_reviewed_observation_does_not_overwrite_newer_price():
    user()
    payload = price()
    now = datetime.now(timezone.utc)
    payload["observed_at"] = (now - timedelta(hours=2)).isoformat()
    response = fixtures.client.post(
        "/api/v1/submissions/prices",
        json=payload,
        headers={"Idempotency-Key": "older-123"},
    )
    response = fixtures.client.post(
        "/api/v1/admin/submissions/" + response.json()["id"] + "/review",
        json={"decision": "APPROVED", "note": "Old observation confirmed"},
        headers=ADMIN,
    )
    assert response.status_code == 200, response.text
    assert response.json()["published_as_current"] is False
    assert fixtures.client.get("/api/v1/prices/current").json()[0]["price_eur"] == 1.25
    history = fixtures.client.get(
        "/api/v1/prices/history", params={"product_id": payload["product_id"]}
    )
    assert history.json()[0]["price_scope"] == "BRANCH"


def test_product_images_and_national_scope_are_separate_from_branches():
    with fixtures.TestingSessionLocal() as db:
        product_id = str(db.scalar(select(Product.id)))
        retailer = db.get(
            __import__("app.models", fromlist=["Retailer"]).Retailer, "TEST"
        )
        retailer.website_url = "https://retailer.example"
        db.commit()
    response = fixtures.client.put(
        "/api/v1/admin/products/" + product_id + "/image",
        json={
            "image_url": "https://retailer.example/product.jpg",
            "source_url": "https://retailer.example/product",
        },
        headers=ADMIN,
    )
    assert response.status_code == 200, response.text
    assert (
        fixtures.client.get("/api/v1/products").json()[0]["image_url"]
        == "https://retailer.example/product.jpg"
    )
    now = datetime.now(timezone.utc)
    response = fixtures.client.post(
        "/api/v1/admin/national-offers",
        json={
            "product_id": product_id,
            "retailer_code": "TEST",
            "price_eur": "1.11",
            "source_reference": "https://retailer.example/product",
            "observed_at": now.isoformat(),
            "valid_until": (now + timedelta(days=1)).isoformat(),
        },
        headers=ADMIN,
    )
    assert response.status_code == 201, response.text
    assert response.json()["branch_id"] is None
    assert (
        fixtures.client.get("/api/v1/national-offers").json()[0]["price_scope"]
        == "NATIONAL_ONLINE"
    )
    assert fixtures.client.get("/api/v1/prices/current").json()[0]["price_eur"] == 1.25


def test_demo_catalog_is_explicit_and_does_not_populate_real_prices(monkeypatch):
    monkeypatch.delenv("ENABLE_DEMO_CATALOG", raising=False)
    assert fixtures.client.get("/api/v1/demo/catalog").status_code == 404
    monkeypatch.setenv("ENABLE_DEMO_CATALOG", "true")
    response = fixtures.client.get("/api/v1/demo/catalog")
    assert response.json()["is_demo"] is True
    assert len(response.json()["products"]) == 3
    for product in response.json()["products"]:
        assert product["price_eur"] is None and product["verified"] is False
        assert (
            fixtures.client.get(product["image_url"]).headers["content-type"]
            == "image/jpeg"
        )
    assert fixtures.client.get("/api/v1/prices/current").json()[0]["price_eur"] == 1.25


def test_basket_comparison_never_ranks_an_incomplete_basket_as_cheapest():
    from app.models import Locality

    with fixtures.TestingSessionLocal() as db:
        product = db.scalar(select(Product))
        locality = db.scalar(select(Locality))
        product_id = str(product.id)
        locality_id = str(locality.id)
        other = Product(
            category_code="FOOD",
            name="Missing price product",
            normalized_name="missing price product",
        )
        db.add(other)
        db.commit()
        other_id = str(other.id)
    response = fixtures.client.post(
        "/api/v1/baskets/compare",
        json={
            "locality_id": locality_id,
            "items": [{"product_id": product_id, "quantity": 2}],
        },
    )
    assert response.status_code == 200, response.text
    # Valid verified promotional price 0.99, two packages.
    result = response.json()
    assert datetime.fromisoformat(result["quoted_at"]).tzinfo is not None
    quote = result["cheapest"]
    assert quote["retailer_name"] == "Test Market"
    assert quote["branch_address"] == "Main street 1"
    assert Decimal(quote["total_eur"]) == Decimal("1.98")
    line, = quote["items"]
    assert (line["product_id"], line["quantity"], line["verified_at"]) == (product_id, 2, None)
    assert Decimal(line["unit_price_eur"]) == Decimal("0.99")
    assert Decimal(line["subtotal_eur"]) == Decimal("1.98")
    response = fixtures.client.post(
        "/api/v1/baskets/compare",
        json={
            "locality_id": locality_id,
            "items": [{"product_id": product_id}, {"product_id": other_id}],
        },
    )
    assert response.json()["cheapest"] is None
    assert response.json()["quotes"][0]["total_eur"] is None
    assert response.json()["quotes"][0]["missing_product_ids"] == [other_id]
    assert response.json()["quotes"][0]["items"][1] == {
        "product_id": other_id, "quantity": 1,
        "unit_price_eur": None, "subtotal_eur": None, "verified_at": None,
    }
