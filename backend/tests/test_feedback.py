"""Feedback cannot become an open relay or report unconfigured delivery success."""

import smtplib
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import feedback

client = TestClient(app)
BODY = {
    "name": "Preview test",
    "email": "sender@example.invalid",
    "phone": "+359 000 000 000",
    "message": "Synthetic feedback integration test.",
}


@pytest.fixture(autouse=True)
def environment(monkeypatch):
    feedback._attempts.clear()
    for key in (
        "FEEDBACK_DELIVERY_ENABLED",
        "FEEDBACK_SMTP_HOST",
        "FEEDBACK_SMTP_USER",
        "FEEDBACK_SMTP_PASSWORD",
        "FEEDBACK_FROM",
    ):
        monkeypatch.delenv(key, raising=False)
    yield
    feedback._attempts.clear()


def configure(monkeypatch):
    for key, value in {
        "FEEDBACK_DELIVERY_ENABLED": "true",
        "FEEDBACK_SMTP_HOST": "smtp.example.invalid",
        "FEEDBACK_SMTP_USER": "test-only",
        "FEEDBACK_SMTP_PASSWORD": "test-only-not-a-real-secret",
        "FEEDBACK_FROM": "app@example.invalid",
    }.items():
        monkeypatch.setenv(key, value)


def test_missing_provider_never_reports_success():
    result = client.get("/api/v1/feedback/availability")
    assert result.json() == {"available": False}
    assert result.headers["cache-control"] == "no-store"
    assert client.post("/api/v1/feedback", json=BODY).status_code == 503


def test_recipient_cannot_be_supplied_and_headers_are_validated(monkeypatch):
    configure(monkeypatch)
    for change in (
        {"recipient": "other@example.invalid"},
        {"email": "bad-email"},
        {"name": "Test\r\nBcc: attacker@example.invalid"},
        {"message": "short"},
    ):
        assert (
            client.post("/api/v1/feedback", json={**BODY, **change}).status_code == 422
        )
    assert not feedback._attempts


def test_smtp_fixed_recipient_reply_to_tls_and_no_secret_in_response(monkeypatch):
    configure(monkeypatch)
    received = {}

    class SMTP:
        def __init__(self, host, port, timeout):
            received.update(host=host, port=port)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def starttls(self, context):
            received["tls"] = bool(context.check_hostname)

        def login(self, user, password):
            received["login"] = True

        def send_message(self, letter):
            received["letter"] = letter
            return {}

    monkeypatch.setattr(smtplib, "SMTP", SMTP)
    result = client.post("/api/v1/feedback", json=BODY)
    assert result.status_code == 202 and result.json() == {"status": "accepted"}
    assert received["letter"]["To"] == "ivo77@duck.com"
    assert received["letter"]["Reply-To"] == BODY["email"]
    assert received["letter"]["From"] == "app@example.invalid"
    assert received["tls"] and received["login"]
    assert "FEEDBACK_" not in result.text and "test-only" not in result.text


def test_provider_failure_and_preview_quota(monkeypatch):
    configure(monkeypatch)

    def fail(payload):
        raise smtplib.SMTPException("provider diagnostic with private details")

    monkeypatch.setattr(feedback, "deliver", fail)
    for _ in range(5):
        result = client.post("/api/v1/feedback", json=BODY)
        assert result.status_code == 503 and "private details" not in result.text
    result = client.post("/api/v1/feedback", json=BODY)
    assert result.status_code == 429 and result.headers["retry-after"] == "600"


def test_configured_but_disabled_provider_never_attempts_delivery(monkeypatch):
    configure(monkeypatch)
    monkeypatch.setenv("FEEDBACK_DELIVERY_ENABLED", "false")

    def forbidden(payload):
        raise AssertionError("Disabled delivery must not send")

    monkeypatch.setattr(feedback, "deliver", forbidden)
    assert client.get("/api/v1/feedback/availability").json() == {"available": False}
    assert client.post("/api/v1/feedback", json=BODY).status_code == 503
    assert not feedback._attempts
