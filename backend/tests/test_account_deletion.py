"""Account erasure: private data removed, shared catalogue provenance kept anonymous."""

from io import BytesIO
from pathlib import Path

import httpx
import pytest
from PIL import Image
from sqlalchemy import func, select

import test_locality_search as fixtures
from app import mobile_auth
from app.auth import Principal, current_user
from app.db import get_db
from app.main import app
from app.marketplace import PriceCache, ReceiptScan
from app.receipts import ReceiptStorage
from app.workflows import ProductIdentificationRequest, ReceiptJob, ReviewSubmission

SESSION = {"X-Auth-Session": "signed.session"}


@pytest.fixture(autouse=True)
def database(tmp_path, monkeypatch):
    previous = dict(app.dependency_overrides)
    if fixtures.engine.dialect.name == "sqlite":
        with fixtures.engine.begin() as connection:
            connection.exec_driver_sql("PRAGMA foreign_keys = ON")
    fixtures.setup_function()
    app.dependency_overrides[get_db] = fixtures.override_get_db
    monkeypatch.setenv("RECEIPT_STORAGE_DIR", str(tmp_path))
    yield
    fixtures.teardown_function()
    if fixtures.engine.dialect.name == "sqlite":
        with fixtures.engine.begin() as connection:
            connection.exec_driver_sql("PRAGMA foreign_keys = OFF")
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setenv(
        "NEON_AUTH_BASE_URL", "https://identity.example.invalid/bgprices/auth"
    )
    state = {"session_user": "alice", "delete_status": 200, "delete_message": "User deleted", "calls": []}

    def request(method, url, **kwargs):
        path = url.split("/auth")[-1]
        state["calls"].append((method, path, kwargs))
        req = httpx.Request(method, url)
        if path == "/get-session":
            return httpx.Response(
                200, json={"user": {"id": state["session_user"]}}, request=req
            )
        if path == "/delete-user":
            return httpx.Response(
                state["delete_status"],
                json={"success": True, "message": state["delete_message"]},
                request=req,
            )
        raise AssertionError(path)

    monkeypatch.setattr(mobile_auth.httpx, "request", request)
    return state


def as_user(name="alice"):
    app.dependency_overrides[current_user] = lambda: Principal(name)


def image(colour):
    out = BytesIO()
    Image.new("RGB", (60, 80), colour).save(out, format="PNG")
    return out.getvalue()


def upload(key, colour):
    return fixtures.client.post(
        "/api/v1/receipts",
        headers={"Idempotency-Key": key},
        files={"file": ("receipt.png", image(colour), "image/png")},
    )


def seed_contributions():
    with fixtures.TestingSessionLocal() as db:
        for owner, key, status in [
            ("alice", "k-pending", "PENDING"),
            ("alice", "k-verified", "VERIFIED"),
            ("bob", "k-bob", "PENDING"),
        ]:
            cache = PriceCache(submitted_price_eur=1, source="USER", status=status)
            db.add(cache)
            db.flush()
            db.add(ReviewSubmission(owner_subject=owner, request_key=key, cache_id=cache.id))
        for owner, barcode, status in [
            ("alice", "3800000000011", "PENDING"),
            ("alice", "3800000000028", "RESOLVED"),
            ("bob", "3800000000035", "PENDING"),
        ]:
            db.add(ProductIdentificationRequest(owner_subject=owner, barcode=barcode, status=status))
        db.commit()


def count(model, **where):
    with fixtures.TestingSessionLocal() as db:
        query = select(func.count()).select_from(model)
        for key, value in where.items():
            query = query.where(getattr(model, key) == value)
        return db.scalar(query)


def provider_calls(state, path):
    return [c for c in state["calls"] if c[1] == path]


def test_requires_authentication_and_session_header(provider):
    assert fixtures.client.delete("/api/v1/account", headers=SESSION).status_code == 401
    assert not provider["calls"]


def test_erases_private_data_keeps_reviewed_history_anonymously(provider):
    as_user("alice")
    assert upload("alice-receipt-1", "white").status_code == 202
    as_user("bob")
    assert upload("bob-receipt-1", "red").status_code == 202
    seed_contributions()
    as_user("alice")
    response = fixtures.client.delete("/api/v1/account", headers=SESSION)
    assert response.status_code == 204
    assert response.headers["cache-control"] == "no-store"
    (_, _, kwargs), = provider_calls(provider, "/delete-user")
    assert kwargs["headers"]["Cookie"].endswith("=signed.session")
    # Alice's receipts and stored images are gone; Bob's are untouched.
    assert count(ReceiptJob, owner_subject="alice") == 0
    assert count(ReceiptJob, owner_subject="bob") == 1
    assert count(ReceiptScan) == 1
    assert len(list(Path(ReceiptStorage().directory).rglob("*.png"))) == 1
    # Pending contributions deleted, reviewed ones unlinked, others untouched.
    assert count(ReviewSubmission, owner_subject="alice") == 0
    assert count(PriceCache, status="PENDING") == 1
    with fixtures.TestingSessionLocal() as db:
        owners = {r.owner_subject for r in db.scalars(select(ReviewSubmission))}
        requests = {r.owner_subject for r in db.scalars(select(ProductIdentificationRequest))}
    assert "alice" not in owners | requests
    assert sum(o.startswith("deleted:") for o in owners) == 1 and "bob" in owners
    assert sum(o.startswith("deleted:") for o in requests) == 1 and "bob" in requests


def test_session_for_another_user_is_rejected_before_any_erasure(provider):
    as_user("alice")
    assert upload("alice-receipt-1", "white").status_code == 202
    provider["session_user"] = "mallory"
    assert fixtures.client.delete("/api/v1/account", headers=SESSION).status_code == 403
    assert count(ReceiptJob, owner_subject="alice") == 1
    assert not provider_calls(provider, "/delete-user")


def test_service_principals_cannot_delete_accounts(provider):
    app.dependency_overrides[current_user] = lambda: Principal("admin-1", "admin")
    assert fixtures.client.delete("/api/v1/account", headers=SESSION).status_code == 403
    assert not provider["calls"]


def test_receipt_being_processed_blocks_erasure(provider):
    as_user("alice")
    assert upload("alice-receipt-1", "white").status_code == 202
    with fixtures.TestingSessionLocal() as db:
        db.scalar(select(ReceiptScan)).status = "PROCESSING"
        db.commit()
    assert fixtures.client.delete("/api/v1/account", headers=SESSION).status_code == 409
    assert count(ReceiptJob, owner_subject="alice") == 1
    assert not provider_calls(provider, "/delete-user")


def test_storage_outage_is_retryable_and_never_deletes_identity(provider, monkeypatch):
    as_user("alice")
    assert upload("alice-receipt-1", "white").status_code == 202
    original = ReceiptStorage.delete
    monkeypatch.setattr(
        ReceiptStorage,
        "delete",
        lambda *a: (_ for _ in ()).throw(OSError("simulation outage")),
    )
    assert fixtures.client.delete("/api/v1/account", headers=SESSION).status_code == 503
    assert not provider_calls(provider, "/delete-user")
    with fixtures.TestingSessionLocal() as db:
        assert db.scalar(select(ReceiptScan)).status == "DELETING"
    monkeypatch.setattr(ReceiptStorage, "delete", original)
    assert fixtures.client.delete("/api/v1/account", headers=SESSION).status_code == 204
    assert count(ReceiptJob, owner_subject="alice") == 0


def test_provider_failure_reports_502_after_data_erased_and_retry_succeeds(provider):
    as_user("alice")
    assert upload("alice-receipt-1", "white").status_code == 202
    provider["delete_status"] = 500
    response = fixtures.client.delete("/api/v1/account", headers=SESSION)
    assert response.status_code == 502 and "erased" in response.json()["detail"]
    assert count(ReceiptJob, owner_subject="alice") == 0
    provider["delete_status"] = 200
    assert fixtures.client.delete("/api/v1/account", headers=SESSION).status_code == 204


def test_provider_verification_email_does_not_confirm_deletion(provider, monkeypatch):
    as_user()
    provider["delete_message"] = "Verification email sent"

    def unexpected_storage(*args):
        pytest.fail("An account without receipts must not require storage")

    monkeypatch.setattr("app.account.ReceiptStorage", unexpected_storage)
    response = fixtures.client.delete("/api/v1/account", headers=SESSION)
    assert response.status_code == 502
    assert provider_calls(provider, "/delete-user")


def test_data_deletion_rejects_guest_and_another_users_session(provider):
    assert fixtures.client.delete("/api/v1/account/data", headers=SESSION).status_code == 401
    as_user("bob")
    assert upload("bob-kept-receipt", "red").status_code == 202
    assert fixtures.client.delete("/api/v1/account/data", headers=SESSION).status_code == 403
    assert count(ReceiptJob, owner_subject="bob") == 1
    assert not provider_calls(provider, "/delete-user")


def test_data_deletion_erases_own_data_without_deleting_profile(provider):
    as_user()
    assert upload("alice-private-receipt", "white").status_code == 202
    seed_contributions()
    for _ in range(2):
        response = fixtures.client.delete("/api/v1/account/data", headers=SESSION)
        assert response.status_code == 204
        assert response.headers["cache-control"] == "no-store"
    assert count(ReceiptJob, owner_subject="alice") == 0
    assert count(ReviewSubmission, owner_subject="alice") == 0
    assert count(ProductIdentificationRequest, owner_subject="alice") == 0
    assert count(ReviewSubmission, owner_subject="bob") == 1
    assert not provider_calls(provider, "/delete-user")
    assert not list(Path(ReceiptStorage().directory).rglob("*.png"))
