"""Rate-limit, proxy-address, upload-quota and receipt-image behaviour."""

from io import BytesIO

import httpx
import pytest
from PIL import Image
from starlette.requests import Request

import test_locality_search as fixtures
from app import auth, mobile_auth
from app.auth import Principal, current_user
from app.db import get_db
from app.main import app
from app.request_limits import RequestLimits, client_address
from fastapi.testclient import TestClient

client = TestClient(app)


def request_with(forwarded=None, peer="10.0.0.1"):
    headers = [(b"x-forwarded-for", forwarded.encode())] if forwarded else []
    return Request(
        {"type": "http", "headers": headers, "client": (peer, 1234), "method": "GET", "path": "/"}
    )


# --- client address behind a proxy ---------------------------------------------


def test_client_address_ignores_forwarded_header_by_default(monkeypatch):
    monkeypatch.delenv("TRUSTED_PROXY_HOPS", raising=False)
    assert client_address(request_with("203.0.113.9")) == "10.0.0.1"


def test_client_address_uses_trusted_hop_and_ignores_spoofed_prefix(monkeypatch):
    monkeypatch.setenv("TRUSTED_PROXY_HOPS", "1")
    # A client prepended "1.2.3.4"; the trusted proxy appended the real address.
    assert client_address(request_with("1.2.3.4, 203.0.113.9")) == "203.0.113.9"
    monkeypatch.setenv("TRUSTED_PROXY_HOPS", "2")
    assert client_address(request_with("203.0.113.9, 198.51.100.7")) == "203.0.113.9"


@pytest.mark.parametrize("header", [None, "", "not-an-ip", "203.0.113.9"])
def test_client_address_falls_back_to_peer_when_header_unusable(monkeypatch, header):
    monkeypatch.setenv("TRUSTED_PROXY_HOPS", "2")
    assert client_address(request_with(header)) == "10.0.0.1"


def test_invalid_hop_setting_is_treated_as_zero(monkeypatch):
    monkeypatch.setenv("TRUSTED_PROXY_HOPS", "many")
    assert client_address(request_with("203.0.113.9")) == "10.0.0.1"


# --- sign-up and sign-in limits ------------------------------------------------


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setattr(mobile_auth, "request_limits", RequestLimits())
    monkeypatch.setenv("NEON_AUTH_BASE_URL", "https://identity.example.invalid/auth")
    calls = []

    def request(method, url, **kwargs):
        calls.append(url)
        path = url.split("/auth")[-1]
        if path == "/sign-in/email":
            return httpx.Response(401, request=httpx.Request(method, url))
        if path == "/sign-up/email":
            return httpx.Response(422, json={}, request=httpx.Request(method, url))
        raise AssertionError(path)

    monkeypatch.setattr(mobile_auth.httpx, "request", request)
    return calls


def test_sign_up_is_rate_limited_before_reaching_the_provider(provider):
    body = {"email": "new@example.invalid", "password": "long-enough-1"}
    for _ in range(5):
        assert client.post("/api/v1/auth/sign-up", json=body).status_code == 422
    limited = client.post("/api/v1/auth/sign-up", json=body)
    assert limited.status_code == 429 and "retry-after" in limited.headers
    assert len(provider) == 5


def test_stranger_cannot_lock_out_a_victim_from_another_address(provider, monkeypatch):
    victim = {"email": "victim@example.invalid", "password": "wrong-password"}
    monkeypatch.setenv("TRUSTED_PROXY_HOPS", "1")
    attacker = {"x-forwarded-for": "198.51.100.66"}
    for _ in range(10):
        assert client.post("/api/v1/auth/sign-in", json=victim, headers=attacker).status_code == 401
    assert client.post("/api/v1/auth/sign-in", json=victim, headers=attacker).status_code == 429
    # The real owner, from a different address, is still allowed to try.
    owner = {"x-forwarded-for": "203.0.113.5"}
    assert client.post("/api/v1/auth/sign-in", json=victim, headers=owner).status_code == 401


def test_distributed_guessing_still_hits_the_per_email_cap(provider, monkeypatch):
    victim = {"email": "victim@example.invalid", "password": "wrong-password"}
    monkeypatch.setenv("TRUSTED_PROXY_HOPS", "1")
    statuses = [
        client.post(
            "/api/v1/auth/sign-in", json=victim, headers={"x-forwarded-for": f"192.0.2.{i}"}
        ).status_code
        for i in range(41)
    ]
    assert statuses[:40] == [401] * 40 and statuses[40] == 429


# --- token audience ------------------------------------------------------------


def test_strict_audience_mode_refuses_when_audience_missing(monkeypatch):
    monkeypatch.setenv("NEON_AUTH_BASE_URL", "https://identity.example.invalid/auth")
    monkeypatch.setenv("AUTH_REQUIRE_AUDIENCE", "true")
    monkeypatch.delenv("AUTH_AUDIENCE", raising=False)

    class Key:
        key = "unused"

    class Jwks:
        def get_signing_key_from_jwt(self, token):
            return Key()

    monkeypatch.setattr(auth, "jwks_client", lambda url: Jwks())
    app.dependency_overrides.pop(current_user, None)
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer abc.def.ghi"})
    assert response.status_code == 503


# --- receipts ------------------------------------------------------------------


@pytest.fixture
def receipts(tmp_path, monkeypatch):
    previous = dict(app.dependency_overrides)
    fixtures.setup_function()
    app.dependency_overrides[get_db] = fixtures.override_get_db
    monkeypatch.setenv("RECEIPT_STORAGE_DIR", str(tmp_path))
    app.dependency_overrides[current_user] = lambda: Principal("alice")
    yield tmp_path
    fixtures.teardown_function()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


def png(size=(8, 8), mode="RGB", color="white"):
    out = BytesIO()
    Image.new(mode, size, color).save(out, format="PNG")
    return out.getvalue()


def upload(data, name="r.png", mime="image/png", headers=None):
    return fixtures.client.post(
        "/api/v1/receipts", files={"file": (name, data, mime)}, headers=headers or {}
    )


def stored_image(root):
    (path,) = list(root.rglob("*.*"))
    return Image.open(path)


def test_exif_rotation_is_applied_before_metadata_is_stripped(receipts):
    photo = Image.new("RGB", (40, 20), "white")  # landscape pixels
    exif = Image.Exif()
    exif[0x0112] = 6  # "rotate 90 degrees clockwise to display upright"
    out = BytesIO()
    photo.save(out, format="JPEG", exif=exif)
    assert upload(out.getvalue(), "r.jpg", "image/jpeg").status_code == 202
    with stored_image(receipts) as saved:
        assert saved.size == (20, 40)
        assert not saved.getexif()


def test_transparent_receipts_are_flattened_onto_white(receipts):
    assert upload(png(mode="RGBA", color=(0, 0, 0, 0))).status_code == 202
    with stored_image(receipts) as saved:
        assert saved.convert("RGB").getpixel((0, 0)) == (255, 255, 255)


def test_daily_quota_blocks_new_uploads_but_not_idempotent_replays(receipts, monkeypatch):
    monkeypatch.setenv("RECEIPT_DAILY_LIMIT", "2")
    first = upload(png(color="red"), headers={"Idempotency-Key": "key-number-1"})
    assert first.status_code == 202
    assert upload(png(color="green")).status_code == 202
    blocked = upload(png(color="blue"))
    assert blocked.status_code == 429 and blocked.headers["retry-after"] == "3600"
    replay = upload(png(color="red"), headers={"Idempotency-Key": "key-number-1"})
    assert replay.status_code == 202 and replay.json()["id"] == first.json()["id"]
    app.dependency_overrides[current_user] = lambda: Principal("bob")
    assert upload(png(color="yellow")).status_code == 202


def test_daily_quota_can_be_disabled_and_ignores_bad_values(receipts, monkeypatch):
    monkeypatch.setenv("RECEIPT_DAILY_LIMIT", "0")
    for shade in range(3):
        assert upload(png(color=(shade, 0, 0))).status_code == 202
    monkeypatch.setenv("RECEIPT_DAILY_LIMIT", "lots")
    from app.receipts import daily_upload_limit

    assert daily_upload_limit() == 30


def test_upload_burst_limit_stops_before_image_decoding(receipts):
    statuses = [upload(b"not an image").status_code for _ in range(21)]
    assert statuses[:20] == [422] * 20 and statuses[20] == 429


# --- identification and price-submission quotas --------------------------------


def gtin13(prefix):
    body = f"{prefix:012d}"
    total = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(body))
    return body + str((10 - total % 10) % 10)


def identify(code):
    return fixtures.client.post("/api/v1/product-identification-requests", json={"barcode": code})


def test_identification_quota_limits_new_requests_not_repeats(receipts, monkeypatch):
    monkeypatch.setenv("IDENTIFICATION_DAILY_LIMIT", "2")
    first, second, third = (gtin13(n) for n in (100, 200, 300))
    assert identify(first).status_code == 201
    assert identify(second).status_code == 201
    blocked = identify(third)
    assert blocked.status_code == 429 and blocked.headers["retry-after"] == "3600"
    assert identify(first).status_code == 201  # existing request is returned, not counted
    app.dependency_overrides[current_user] = lambda: Principal("bob")
    assert identify(third).status_code == 201


def test_price_submission_quota_spares_replays_and_other_people(receipts, monkeypatch):
    from test_write_workflows import price

    monkeypatch.setenv("SUBMISSION_DAILY_LIMIT", "2")
    body = price()

    def submit(key):
        return fixtures.client.post(
            "/api/v1/submissions/prices", json=body, headers={"Idempotency-Key": key}
        )

    assert submit("quota-key-0001").status_code == 201
    assert submit("quota-key-0002").status_code == 201
    blocked = submit("quota-key-0003")
    assert blocked.status_code == 429 and blocked.headers["retry-after"] == "3600"
    assert submit("quota-key-0001").status_code == 201  # idempotent replay
    app.dependency_overrides[current_user] = lambda: Principal("bob")
    assert submit("quota-key-0004").status_code == 201


def test_quota_limits_can_be_disabled_or_misconfigured(monkeypatch):
    from app.quotas import env_limit

    monkeypatch.setenv("SUBMISSION_DAILY_LIMIT", "0")
    assert env_limit("SUBMISSION_DAILY_LIMIT", 200) == 0
    monkeypatch.setenv("SUBMISSION_DAILY_LIMIT", "-5")
    assert env_limit("SUBMISSION_DAILY_LIMIT", 200) == 0
    monkeypatch.setenv("SUBMISSION_DAILY_LIMIT", "many")
    assert env_limit("SUBMISSION_DAILY_LIMIT", 200) == 200
