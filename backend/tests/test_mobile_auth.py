"""Managed session bridge contract, without real users or leaked provider responses."""

import httpx
import pytest
from app.main import app
from fastapi.testclient import TestClient
from app import mobile_auth

client = TestClient(app)
COOKIE = mobile_auth.COOKIE


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setenv(
        "NEON_AUTH_BASE_URL", "https://identity.example.invalid/bgprices/auth"
    )
    calls = []

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        path = url.split("/auth")[-1]
        if path in ("/sign-in/email", "/sign-up/email"):
            return httpx.Response(
                200,
                json={
                    "user": {
                        "id": "alice",
                        "email": "alice@example.invalid",
                        "name": "Alice",
                    }
                },
                headers={
                    "set-cookie": COOKIE + "=signed.session; Path=/; Secure; HttpOnly"
                },
                request=httpx.Request(method, url),
            )
        if path == "/token":
            return httpx.Response(
                200,
                json={"token": "short-lived-jwt"},
                request=httpx.Request(method, url),
            )
        if path == "/get-session":
            return httpx.Response(
                200,
                request=httpx.Request(method, url),
                json={
                    "user": {
                        "id": "alice",
                        "email": "alice@example.invalid",
                        "name": "Alice",
                    }
                },
            )
        if path == "/sign-out":
            return httpx.Response(
                200, json={"success": True}, request=httpx.Request(method, url)
            )
        raise AssertionError(path)

    monkeypatch.setattr(mobile_auth.httpx, "request", request)
    return calls


def test_signin_restore_and_signout_use_provider_signed_cookie(provider):
    r = client.post(
        "/api/v1/auth/sign-in",
        json={"email": "alice@example.invalid", "password": "simulation-password"},
    )
    assert r.status_code == 200, r.text
    assert r.headers["cache-control"] == "no-store"
    assert r.json()["access_token"] == "short-lived-jwt"
    assert r.json()["session"] == "signed.session"
    assert provider[1][2]["headers"]["Cookie"] == COOKIE + "=signed.session"
    assert all(c[2]["follow_redirects"] is False for c in provider)
    headers = {"X-Auth-Session": r.json()["session"]}
    assert (
        client.post("/api/v1/auth/refresh", headers=headers).json()["user"]["id"]
        == "alice"
    )
    assert client.post("/api/v1/auth/sign-out", headers=headers).json()["success"]


def test_errors_are_private_and_bad_session_rejected_before_network(
    provider, monkeypatch
):
    assert (
        client.post(
            "/api/v1/auth/refresh",
            headers={"X-Auth-Session": "bad; Other-Cookie=inject"},
        ).status_code
        == 401
    )
    assert not provider
    monkeypatch.setattr(
        mobile_auth.httpx,
        "request",
        lambda *a, **kw: httpx.Response(
            401, json={"message": "secret provider details"}
        ),
    )
    r = client.post(
        "/api/v1/auth/sign-in",
        json={"email": "alice@example.invalid", "password": "wrong-password"},
    )
    assert r.status_code == 401 and "secret" not in r.text
    assert r.headers["cache-control"] == "no-store"
    monkeypatch.setattr(
        mobile_auth.httpx,
        "request",
        lambda *a, **kw: httpx.Response(
            200,
            content=b"null",
            request=httpx.Request("GET", "https://identity.example.invalid"),
        ),
    )
    assert (
        client.post(
            "/api/v1/auth/refresh", headers={"X-Auth-Session": "expired"}
        ).status_code
        == 401
    )


def test_provider_outage_fails_closed(monkeypatch):
    monkeypatch.setenv("NEON_AUTH_BASE_URL", "https://identity.example.invalid/auth")

    def failed(*a, **kw):
        raise httpx.ConnectTimeout("simulation")

    monkeypatch.setattr(mobile_auth.httpx, "request", failed)
    r = client.post(
        "/api/v1/auth/sign-in",
        json={"email": "alice@example.invalid", "password": "simulation-password"},
    )
    assert r.status_code == 503 and r.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    ("provider_code", "expected_status"),
    [("USER_ALREADY_EXISTS_USE_ANOTHER_EMAIL", 409), ("OTHER", 422)],
)
def test_registration_distinguishes_existing_account(provider, monkeypatch, provider_code, expected_status):
    monkeypatch.setattr(
        mobile_auth.httpx,
        "request",
        lambda *args, **kwargs: httpx.Response(
            422, json={"code": provider_code, "message": "private provider payload"}
        ),
    )
    response = client.post(
        "/api/v1/auth/sign-up",
        json={"email": "alice@example.invalid", "password": "simulation-password"},
    )
    assert response.status_code == expected_status
    assert "private provider payload" not in response.text


def test_existing_short_password_reaches_provider_but_new_one_is_rejected(provider):
    body = {"email": "alice@example.invalid", "password": "short"}
    assert client.post("/api/v1/auth/sign-in", json=body).status_code == 200
    assert client.post("/api/v1/auth/sign-up", json=body).status_code == 422


def test_sign_in_attempts_are_limited_per_account_before_the_provider(provider):
    body = {"email": "Alice@Example.invalid", "password": "wrong-password"}
    for _ in range(10):
        assert client.post("/api/v1/auth/sign-in", json=body).status_code == 200
    sent = len(provider)
    r = client.post("/api/v1/auth/sign-in", json=dict(body, email="ALICE@example.invalid"))
    assert r.status_code == 429 and r.headers["retry-after"] == "600"
    assert r.headers["cache-control"] == "no-store"
    assert len(provider) == sent  # case variants share one bucket; no provider call
    other = dict(body, email="bob@example.invalid")
    assert client.post("/api/v1/auth/sign-in", json=other).status_code == 200


def test_total_sign_in_volume_is_capped(provider, monkeypatch):
    monkeypatch.setattr(mobile_auth, "_total", mobile_auth.SlidingWindow(3, 60))
    codes = [
        client.post(
            "/api/v1/auth/sign-in",
            json={"email": f"user{i}@example.invalid", "password": "x"},
        ).status_code
        for i in range(4)
    ]
    assert codes == [200, 200, 200, 429]
