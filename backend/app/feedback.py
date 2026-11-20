"""Fixed-recipient feedback; credentials remain in deployment secrets."""

import os
import re
import smtplib
from email.message import EmailMessage

import httpx
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .ratelimit import SlidingWindow

router = APIRouter(prefix="/api/v1/feedback")
RECIPIENT = "ivo77@duck.com"
# Global bounded quota for this single-instance preview; no spoofable IP headers.
_attempts = SlidingWindow(5, 600)


class Feedback(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=254)
    phone: str | None = Field(default=None, max_length=40)
    message: str = Field(min_length=10, max_length=5000)

    @field_validator("name", "email", "phone")
    @classmethod
    def no_header_controls(cls, value):
        if value and any(ord(c) < 32 or ord(c) == 127 for c in value):
            raise ValueError("Invalid contact details")
        return value

    @field_validator("email")
    @classmethod
    def email_shape(cls, value):
        if not re.fullmatch(r"[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+", value):
            raise ValueError("Invalid email")
        return value


def provider():
    return os.getenv("FEEDBACK_PROVIDER", "brevo").strip().lower()


def configured():
    if os.getenv("FEEDBACK_DELIVERY_ENABLED", "false").lower() != "true":
        return False
    if provider() == "brevo":
        required = ("FEEDBACK_BREVO_API_KEY", "FEEDBACK_FROM")
    elif provider() == "smtp":
        required = (
            "FEEDBACK_SMTP_HOST",
            "FEEDBACK_SMTP_USER",
            "FEEDBACK_SMTP_PASSWORD",
            "FEEDBACK_FROM",
        )
    else:
        return False
    return all(os.getenv(key) for key in required)


def content(payload: Feedback):
    return f"Име: {payload.name}\nТелефон: {payload.phone or '—'}\nЕл. поща: {payload.email}\n\n{payload.message}"


def deliver(payload: Feedback):
    if provider() == "brevo":
        response = httpx.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": os.environ["FEEDBACK_BREVO_API_KEY"]},
            json={
                "sender": {"name": "Спестовник", "email": os.environ["FEEDBACK_FROM"]},
                "to": [{"email": RECIPIENT}],
                "replyTo": {"email": payload.email},
                "subject": "Спестовник — Обратна връзка",
                "textContent": content(payload),
            },
            timeout=10,
        )
        if response.status_code != 201:
            raise ValueError("Email provider unavailable")
        acknowledgement = response.json()
        receipt = (
            acknowledgement.get("messageId")
            if isinstance(acknowledgement, dict)
            else None
        )
        if not isinstance(receipt, str) or not receipt.strip():
            raise ValueError("Email provider did not acknowledge acceptance")
        return
    deliver_smtp(payload)


def deliver_smtp(payload: Feedback):
    letter = EmailMessage()
    letter["Subject"] = "Спестовник — Обратна връзка"
    letter["From"] = os.environ["FEEDBACK_FROM"]
    letter["To"] = RECIPIENT
    letter["Reply-To"] = payload.email
    letter.set_content(content(payload))
    port = int(os.getenv("FEEDBACK_SMTP_PORT", "587"))
    # Verified TLS only; no plaintext credentials or caller-chosen recipients.
    import ssl

    context = ssl.create_default_context()
    transport = smtplib.SMTP_SSL if port == 465 else smtplib.SMTP
    options = {"context": context} if port == 465 else {}
    with transport(
        os.environ["FEEDBACK_SMTP_HOST"], port, timeout=10, **options
    ) as smtp:
        if port != 465:
            smtp.starttls(context=context)
        smtp.login(
            os.environ["FEEDBACK_SMTP_USER"], os.environ["FEEDBACK_SMTP_PASSWORD"]
        )
        if smtp.send_message(letter):
            raise smtplib.SMTPException("Recipient refused")


@router.get("/availability")
def availability(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return {"available": configured()}


@router.post("", status_code=202)
def send(payload: Feedback, response: Response):
    response.headers["Cache-Control"] = "no-store"
    if not configured():
        raise HTTPException(503, "Feedback is temporarily unavailable")
    _attempts.hit()
    try:
        deliver(payload)
    except (OSError, ValueError, smtplib.SMTPException, httpx.HTTPError):
        raise HTTPException(503, "Feedback is temporarily unavailable") from None
    # Provider acceptance is not proof of final mailbox delivery.
    return {"status": "accepted"}
