from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
import jwt
import pytest

from app import auth
from app.main import app


@pytest.fixture
def signing(monkeypatch):
    previous = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    key = Ed25519PrivateKey.generate()
    monkeypatch.setenv("NEON_AUTH_BASE_URL", "https://auth.example/bgprices/auth")
    monkeypatch.delenv("AUTH_AUDIENCE", raising=False)
    monkeypatch.delenv("ADMIN_SUBJECTS", raising=False)

    class Keys:
        def get_signing_key_from_jwt(self, token):
            return SimpleNamespace(key=key.public_key())

    monkeypatch.setattr(auth, "jwks_client", lambda url: Keys())

    def token(**fields):
        now = datetime.now(timezone.utc)
        return jwt.encode(
            dict(
                sub="user-one",
                iss="https://auth.example",
                iat=now,
                exp=now + timedelta(minutes=15),
                **fields,
            ),
            key,
            algorithm="EdDSA",
        )

    yield key, token
    app.dependency_overrides.update(previous)


def test_valid_managed_token_and_no_claim_based_admin_escalation(signing):
    key, token = signing
    c = TestClient(app)
    response = c.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer " + token(role="admin")}
    )
    assert response.json() == {"subject": "user-one", "role": "user"}
    assert (
        c.get(
            "/api/v1/admin/submissions",
            headers={"Authorization": "Bearer " + token(role="admin")},
        ).status_code
        == 403
    )


def test_expired_wrong_issuer_forged_and_unsigned_tokens_rejected(signing):
    key, token = signing
    c = TestClient(app)
    claims = {
        "sub": "user-one",
        "iss": "https://other.example",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=1),
    }
    wrong = jwt.encode(claims, key, algorithm="EdDSA")
    claims["iss"] = "https://auth.example"
    claims["exp"] = datetime.now(timezone.utc) - timedelta(minutes=1)
    expired = jwt.encode(claims, key, algorithm="EdDSA")
    forged = jwt.encode(claims, Ed25519PrivateKey.generate(), algorithm="EdDSA")
    unsigned = jwt.encode(claims, key=None, algorithm="none")
    for value in [wrong, expired, forged, unsigned, "not-a-jwt"]:
        assert (
            c.get(
                "/api/v1/auth/me", headers={"Authorization": "Bearer " + value}
            ).status_code
            == 401
        )


def test_admin_role_only_from_operator_allowlist(signing, monkeypatch):
    key, token = signing
    monkeypatch.setenv("ADMIN_SUBJECTS", "user-one")
    response = TestClient(app).get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer " + token()}
    )
    assert response.json()["role"] == "admin"


def test_missing_auth_config_fails_closed(monkeypatch):
    previous = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        monkeypatch.delenv("NEON_AUTH_BASE_URL", raising=False)
        assert (
            TestClient(app)
            .get("/api/v1/auth/me", headers={"Authorization": "Bearer any-token"})
            .status_code
            == 503
        )
    finally:
        app.dependency_overrides.update(previous)
