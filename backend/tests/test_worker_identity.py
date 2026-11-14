from datetime import datetime, timedelta, timezone
from io import BytesIO
from types import SimpleNamespace

from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from PIL import Image
import jwt
import pytest

import test_locality_search as fixtures
from app.main import app
from app.db import get_db
from app.auth import Principal, current_user
from app import worker_api


@pytest.fixture
def identity(monkeypatch, tmp_path):
    previous = dict(app.dependency_overrides)
    fixtures.setup_function()
    app.dependency_overrides[get_db] = fixtures.override_get_db
    app.dependency_overrides[current_user] = lambda: Principal("receipt-owner")
    monkeypatch.setenv("RECEIPT_STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("RECEIPT_WORKER_OIDC_ENABLED", "true")
    monkeypatch.setenv(
        "RECEIPT_WORKER_AUDIENCE", "https://spestoslav-api.onrender.com/receipt-worker"
    )
    monkeypatch.setenv("ADMIN_API_KEY", "worker-test-" + ("a" * 40))
    key = generate_private_key(65537, 2048)

    class Keys:
        def get_signing_key_from_jwt(self, token):
            return SimpleNamespace(key=key.public_key())

    monkeypatch.setattr(worker_api, "jwks_client", lambda url: Keys())
    now = datetime.now(timezone.utc)
    claims = {
        "iss": worker_api.ISSUER,
        "aud": "https://spestoslav-api.onrender.com/receipt-worker",
        "sub": "repo:Per5on@162897472/spestoslav@1457549969:ref:refs/heads/main",
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=5),
        "repository_id": "1457549969",
        "repository_owner_id": "162897472",
        "ref": "refs/heads/main",
        "workflow_ref": "Per5on/spestoslav/.github/workflows/backend-workers.yml@refs/heads/main",
        "event_name": "workflow_dispatch",
        "run_id": "1234",
        "run_attempt": "1",
        "runner_environment": "github-hosted",
    }

    def token(**updates):
        return jwt.encode(dict(claims, **updates), key, algorithm="RS256")

    yield token
    fixtures.teardown_function()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


def test_oidc_worker_receives_only_a_leased_image_and_completes_once(identity):
    c = fixtures.client
    headers = {"Authorization": "Bearer " + identity()}
    image = BytesIO()
    Image.new("RGB", (10, 10), "white").save(image, format="PNG")
    uploaded = c.post(
        "/api/v1/receipts", files={"file": ("r.png", image.getvalue(), "image/png")}
    )
    assert uploaded.status_code == 202
    claimed = c.post("/internal/receipt-worker/claim", headers=headers)
    assert claimed.status_code == 200, claimed.text
    job = claimed.json()["job"]
    assert set(job) == {"id", "lease"}
    scoped = dict(headers, **{"X-Receipt-Lease": job["lease"]})
    path = "/internal/receipt-worker/jobs/" + job["id"]
    assert c.get(path + "/image", headers=scoped).content == image.getvalue()
    assert c.get(path + "/image", headers=headers).status_code == 403
    other = dict(scoped, Authorization="Bearer " + identity(run_id="other-run"))
    assert c.get(path + "/image", headers=other).status_code == 403
    assert (
        c.post(path + "/complete", headers=scoped, json={"text": "MILK 1.34"}).json()[
            "status"
        ]
        == "NEEDS_REVIEW"
    )
    assert (
        c.post(
            path + "/complete", headers=scoped, json={"text": "duplicate"}
        ).status_code
        == 409
    )
    assert c.post("/internal/receipt-worker/claim", headers=headers).json() == {
        "job": None
    }
    result = c.get("/api/v1/receipts/" + uploaded.json()["id"]).json()
    assert result["status"] == "NEEDS_REVIEW" and len(result["items"]) == 1
    assert c.get("/api/v1/prices/current").json()[0]["price_eur"] == 1.25


@pytest.mark.parametrize(
    "change",
    [
        {"repository_id": "123"},
        {"repository_owner_id": "123"},
        {"ref": "refs/heads/attacker"},
        {
            "workflow_ref": "Per5on/spestoslav/.github/workflows/other.yml@refs/heads/main"
        },
        {"event_name": "pull_request"},
        {"runner_environment": "self-hosted"},
        {"sub": "repo:attacker/spestoslav:ref:refs/heads/main"},
    ],
)
def test_other_repositories_branches_workflows_and_events_are_denied(identity, change):
    result = fixtures.client.post(
        "/internal/receipt-worker/claim",
        headers={"Authorization": "Bearer " + identity(**change)},
    )
    assert result.status_code == 403


def test_wrong_audience_expiry_and_disabled_worker_fail_closed(identity, monkeypatch):
    for updates in [
        {"aud": "other-app"},
        {"exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
    ]:
        assert (
            fixtures.client.post(
                "/internal/receipt-worker/claim",
                headers={"Authorization": "Bearer " + identity(**updates)},
            ).status_code
            == 401
        )
    monkeypatch.setenv("RECEIPT_WORKER_OIDC_ENABLED", "false")
    assert (
        fixtures.client.post(
            "/internal/receipt-worker/claim",
            headers={"Authorization": "Bearer " + identity()},
        ).status_code
        == 503
    )


def test_expired_exhausted_claim_is_finalized_without_publishing(identity):
    from sqlalchemy import select
    from app.workflows import ReceiptJob
    from app.marketplace import ReceiptScan

    c = fixtures.client
    image = BytesIO()
    Image.new("RGB", (5, 5)).save(image, format="PNG")
    uploaded = c.post(
        "/api/v1/receipts", files={"file": ("r.png", image.getvalue(), "image/png")}
    )
    with fixtures.TestingSessionLocal() as db:
        job = db.scalar(select(ReceiptJob))
        scan = db.get(ReceiptScan, job.scan_id)
        job.attempts = 3
        job.claimed_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        scan.status = "PROCESSING"
        db.commit()
    response = c.post(
        "/internal/receipt-worker/claim",
        headers={"Authorization": "Bearer " + identity()},
    )
    assert response.json() == {"job": None}
    assert (
        c.get("/api/v1/receipts/" + uploaded.json()["id"]).json()["status"] == "FAILED"
    )


def test_runner_requests_fresh_identity_and_preserves_endpoint_query(
    monkeypatch, capsys
):
    import importlib.util
    from pathlib import Path
    import httpx

    spec = importlib.util.spec_from_file_location(
        "remote_worker",
        Path(__file__).resolve().parents[2] / "scripts/run_remote_receipt_worker.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv("API_BASE_URL", "https://spestoslav-api.onrender.com")
    monkeypatch.setenv(
        "ACTIONS_ID_TOKEN_REQUEST_URL",
        "https://pipelines.actions.githubusercontent.com/idtoken?api-version=2.0",
    )
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "runner-internal-token")
    monkeypatch.setattr("sys.argv", ["worker", "--max-jobs", "1"])
    seen = []

    def handler(request):
        seen.append(request)
        if request.url.host == "pipelines.actions.githubusercontent.com":
            assert request.url.params["api-version"] == "2.0"
            assert (
                request.url.params["audience"]
                == "https://spestoslav-api.onrender.com/receipt-worker"
            )
            return httpx.Response(200, json={"value": "test-identity-token"})
        assert request.headers["Authorization"] == "Bearer test-identity-token"
        assert request.url.path == "/internal/receipt-worker/claim"
        return httpx.Response(200, json={"job": None})

    original = httpx.Client
    monkeypatch.setattr(
        module.httpx,
        "Client",
        lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs),
    )
    module.main()
    assert len(seen) == 2
    assert "processed 0 jobs" in capsys.readouterr().out
