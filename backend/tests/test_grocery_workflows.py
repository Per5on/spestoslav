"""Representative mock shopping journey, with real API/storage/review behaviour."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from io import BytesIO
from pathlib import Path
import importlib.util
import pytest
from PIL import Image
from sqlalchemy import select, func, update
import test_locality_search as fixtures
from app.main import app
from app.db import get_db
from app.auth import Principal, current_user
from app.grocery import GroceryIdentity, GroceryGroup
from app.models import Product, StoreBranch
from app.marketplace import CurrentPrice, Promotion
from app.receipts import ReceiptStorage
from app.receipt_worker import process_one

spec = importlib.util.spec_from_file_location(
    "grocery_import",
    Path(__file__).resolve().parents[2] / "scripts/import_grocery_catalog.py",
)
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


@pytest.fixture(autouse=True)
def database(tmp_path, monkeypatch):
    previous = dict(app.dependency_overrides)
    fixtures.setup_function()
    app.dependency_overrides[get_db] = fixtures.override_get_db
    monkeypatch.setenv("RECEIPT_STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("ADMIN_API_KEY", "simulation-admin-" + 40 * "a")
    yield
    fixtures.teardown_function()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


def as_user(name="alice"):
    app.dependency_overrides[current_user] = lambda: Principal(name)


def image(colour="white"):
    out = BytesIO()
    picture = Image.new("RGB", (60, 80), colour)
    exif = Image.Exif()
    exif[270] = "private metadata to remove"
    picture.save(out, format="PNG", exif=exif)
    return out.getvalue()


def upload(key="scenario-upload-001", data=None):
    return fixtures.client.post(
        "/api/v1/receipts",
        headers={"Idempotency-Key": key},
        files={"file": ("receipt.png", data or image(), "image/png")},
    )


def test_1000_source_products_idempotency_groups_and_search():
    data = importer.load_catalog()
    with fixtures.TestingSessionLocal.begin() as db:
        importer.import_catalog(db, data)
    with fixtures.TestingSessionLocal.begin() as db:
        importer.import_catalog(db, data)
        assert db.scalar(select(func.count()).select_from(GroceryIdentity)) == 1000
        assert db.scalar(select(func.count()).select_from(GroceryGroup)) == 6
        imported = db.scalars(select(Product).join(GroceryIdentity)).all()
        assert all(p.barcode is None for p in imported)
        assert not db.scalars(
            select(CurrentPrice).where(
                CurrentPrice.product_id.in_([p.id for p in imported])
            )
        ).all()
    snapshot = fixtures.client.get("/api/v1/catalog/groceries")
    assert snapshot.status_code == 200
    assert snapshot.headers["cache-control"] == "public, max-age=300"
    products = snapshot.json()["products"]
    assert len(products) == 1000
    assert all(p["source_url"] == "https://burlex.bg/kolkostruva/" for p in products)
    categories_by_code = {p["source_product_code"]: p["source_category"] for p in data["products"]}
    assert all(p["source_category"] == categories_by_code[p["source_product_code"]] for p in products)
    assert len({p["id"] for p in products}) == 1000
    groups = fixtures.client.get("/api/v1/grocery/groups").json()
    assert len(groups) == 6 and sum(g["count"] for g in groups) == 1000
    target = products[-1]
    found = fixtures.client.get(
        "/api/v1/products",
        params={"q": target["name"], "group_code": target["group_code"]},
    ).json()
    assert target in found
    assert fixtures.client.get("/api/v1/products", params={"q": "%_"}).json() == []


def test_private_receipt_replay_ownership_metadata_and_deletion():
    as_user()
    body = image()
    created = upload(data=body)
    assert created.status_code == 202
    identity = created.json()["id"]
    path = "/api/v1/receipts/" + identity
    assert upload(data=body).json()["id"] == identity
    assert upload(data=image("red")).status_code == 409
    assert len(fixtures.client.get("/api/v1/receipts").json()) == 1
    stored = fixtures.client.get(path + "/image")
    assert stored.status_code == 200
    with Image.open(BytesIO(stored.content)) as pic:
        assert not pic.getexif()
    assert fixtures.client.get(path).headers["cache-control"] == "no-store"
    as_user("bob")
    assert fixtures.client.get("/api/v1/receipts").json() == []
    for suffix in ["", "/image"]:
        assert fixtures.client.get(path + suffix).status_code == 404
    assert fixtures.client.delete(path).status_code == 404
    as_user()
    assert fixtures.client.delete(path).status_code == 204
    assert fixtures.client.get(path).status_code == 404
    assert not list(Path(ReceiptStorage().directory).rglob("*.png"))


def test_failed_object_deletion_is_retryable_and_not_processed(monkeypatch):
    as_user()
    identity = upload().json()["id"]
    path = "/api/v1/receipts/" + identity
    original = ReceiptStorage.delete
    monkeypatch.setattr(
        ReceiptStorage,
        "delete",
        lambda *args: (_ for _ in ()).throw(OSError("simulation outage")),
    )
    assert fixtures.client.delete(path).status_code == 503
    assert fixtures.client.get(path).json()["status"] == "DELETING"
    assert fixtures.client.get(path + "/image").status_code == 410
    assert (
        process_one(fixtures.TestingSessionLocal, ocr=lambda _: "Never processed")
        is False
    )
    monkeypatch.setattr(ReceiptStorage, "delete", original)
    assert fixtures.client.delete(path).status_code == 204


@pytest.mark.parametrize(
    "currency,expected", [("EUR", "2.40"), ("ЕВРО", "2.40"), ("BGN", None), ("ЛВ.", None), ("", None)]
)
def test_ocr_ignores_totals_discounts_and_unknown_currency(currency, expected):
    as_user()
    identity = upload().json()["id"]
    text = f"MILK 2.40 {currency}\nTOTAL 2.40 {currency}\nCASH 3.00 {currency}\nCHANGE 0.60 {currency}\nDISCOUNT -0.10 {currency}\nFREE 0.00 {currency}"
    assert process_one(fixtures.TestingSessionLocal, ocr=lambda _: text)
    data = fixtures.client.get("/api/v1/receipts/" + identity).json()
    assert data["status"] == "NEEDS_REVIEW"
    assert len(data["items"]) == 1
    actual = data["items"][0]["line_total_eur"]
    assert (Decimal(actual) if actual is not None else None) == (
        Decimal(expected) if expected is not None else None
    )
    assert fixtures.client.get("/api/v1/prices/current").json()[0]["price_eur"] == 1.25


def test_mock_receipt_price_review_and_complete_basket_only():
    as_user()
    identity = upload().json()["id"]
    assert process_one(
        fixtures.TestingSessionLocal, ocr=lambda _: "MILK 1.10 EUR\nTOTAL 1.10 EUR"
    )
    detail = fixtures.client.get("/api/v1/receipts/" + identity).json()
    item = detail["items"][0]
    with fixtures.TestingSessionLocal.begin() as db:
        product = db.scalar(select(Product))
        branch = db.scalar(select(StoreBranch))
        product_id, branch_id, locality = (
            str(product.id),
            str(branch.id),
            str(branch.locality_id),
        )
        # Another shop has only one of the requested products: never rank its partial total.
        other = StoreBranch(
            retailer_code=branch.retailer_code,
            locality_id=branch.locality_id,
            address="Simulation second shop",
        )
        db.add(other)
        db.flush()
        second = Product(
            category_code=product.category_code,
            name="Simulation oil",
            normalized_name="simulation oil",
        )
        db.add(second)
        db.flush()
        second_id = str(second.id)
        now = datetime.now(timezone.utc)
        db.execute(update(Promotion).values(ends_at=now - timedelta(seconds=1)))
        db.add_all(
            [
                CurrentPrice(
                    product_id=product.id,
                    branch_id=other.id,
                    price_eur=Decimal(".50"),
                    source="SIMULATION",
                    verified_at=now,
                ),
                CurrentPrice(
                    product_id=second.id,
                    branch_id=branch.id,
                    price_eur=Decimal("3"),
                    source="SIMULATION",
                    verified_at=now,
                ),
            ]
        )
    payload = {
        "locality_id": locality,
        "items": [
            {"product_id": product_id, "quantity": 2},
            {"product_id": second_id, "quantity": 1},
        ],
    }
    before = fixtures.client.post("/api/v1/baskets/compare", json=payload).json()
    assert before["cheapest"]["branch_id"] == branch_id and Decimal(
        before["cheapest"]["total_eur"]
    ) == Decimal("5.50")
    submission = fixtures.client.post(
        f"/api/v1/receipts/{identity}/items/{item['id']}/submit-price",
        json={
            "product_id": product_id,
            "branch_id": branch_id,
            "price_eur": "1.10",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        },
    )
    assert submission.status_code == 201, submission.text
    assert (
        fixtures.client.post("/api/v1/baskets/compare", json=payload).json()[
            "cheapest"
        ]["total_eur"]
        == before["cheapest"]["total_eur"]
    )
    approved = fixtures.client.post(
        "/api/v1/admin/submissions/" + submission.json()["id"] + "/review",
        headers={"X-Admin-Key": "simulation-admin-" + 40 * "a"},
        json={
            "decision": "APPROVED",
            "note": "Checked synthetic receipt in isolated scenario",
        },
    )
    assert approved.status_code == 200, approved.text
    result = fixtures.client.post("/api/v1/baskets/compare", json=payload).json()
    assert Decimal(result["cheapest"]["total_eur"]) == Decimal("5.20")
    assert any(not q["complete"] and q["total_eur"] is None for q in result["quotes"])
    assert result["shipping_and_travel_included"] is False
    assert (
        fixtures.client.get("/api/v1/receipts/" + identity).json()["items"][0]["status"]
        == "VERIFIED"
    )


def test_gtin_lookup_validates_aliases_inactive_and_conflicts():
    from app.models import Category
    from sqlalchemy import update

    c = fixtures.client
    assert c.get("/api/v1/products/barcode/3800000000003").status_code == 200
    assert c.get("/api/v1/products/barcode/03800000000003").status_code == 200
    for value in ["3800000000000", "12345", "1234567890", "not-a-barcode"]:
        assert c.get("/api/v1/products/barcode/" + value).status_code == 422
    with fixtures.TestingSessionLocal.begin() as db:
        other = Product(
            category_code="FOOD",
            name="Conflicting simulation product",
            normalized_name="conflict",
            barcode="03800000000003",
        )
        db.add(other)
    assert c.get("/api/v1/products/barcode/3800000000003").status_code == 409
    with fixtures.TestingSessionLocal.begin() as db:
        db.execute(update(Category).values(active=False))
    assert c.get("/api/v1/products/barcode/3800000000003").status_code == 404


def test_real_bulgarian_ocr_keeps_only_product_totals(tmp_path):
    import shutil, subprocess, importlib.util

    if (
        not shutil.which("tesseract")
        or "bul"
        not in subprocess.run(
            ["tesseract", "--list-langs"], capture_output=True, text=True
        ).stdout.split()
    ):
        pytest.skip("Install Bulgarian Tesseract data for the real OCR fixture check")
    spec = importlib.util.spec_from_file_location(
        "mock_images",
        Path(__file__).resolve().parents[2] / "scripts/generate_mock_images.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    out = BytesIO()
    module.receipt_image().save(out, format="PNG")
    as_user()
    identity = upload("actual-ocr-fixture", out.getvalue()).json()["id"]
    assert process_one(fixtures.TestingSessionLocal)
    result = fixtures.client.get("/api/v1/receipts/" + identity).json()
    assert result["status"] == "NEEDS_REVIEW"
    assert len(result["items"]) == 2, result
    assert sorted(Decimal(row["line_total_eur"]) for row in result["items"]) == [
        Decimal("2.20"),
        Decimal("3.00"),
    ]
    assert fixtures.client.get("/api/v1/prices/current").json()[0]["price_eur"] == 1.25


def test_slow_receipt_storage_does_not_block_health(monkeypatch):
    import asyncio
    import threading
    import httpx

    as_user()
    started, release = threading.Event(), threading.Event()
    original_put = ReceiptStorage.put

    def slow_put(self, *args):
        started.set()
        assert release.wait(3), "Test did not release simulated storage"
        return original_put(self, *args)

    monkeypatch.setattr(ReceiptStorage, "put", slow_put)

    async def scenario():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://local-test"
        ) as client:
            task = asyncio.create_task(client.post(
                "/api/v1/receipts",
                headers={"Idempotency-Key": "responsive-upload-001"},
                files={"file": ("receipt.png", image(), "image/png")},
            ))
            try:
                assert await asyncio.to_thread(started.wait, 2)
                assert not task.done(), "Storage blocked the API event loop"
                health = await asyncio.wait_for(client.get("/health"), timeout=1)
                assert health.status_code == 200
                assert not task.done()
            finally:
                release.set()
            assert (await task).status_code == 202

    asyncio.run(scenario())
