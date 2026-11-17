"""Fixed-recipient feedback; credentials remain in deployment secrets."""

from collections import deque
from email.message import EmailMessage
import os
import re
import smtplib
from threading import Lock
import time

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator

router = APIRouter(prefix="/api/v1/feedback")
RECIPIENT = "ivo77@duck.com"
_attempts: deque[float] = deque()
_lock = Lock()


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


def configured():
    return all(
        os.getenv(k)
        for k in (
            "FEEDBACK_SMTP_HOST",
            "FEEDBACK_SMTP_USER",
            "FEEDBACK_SMTP_PASSWORD",
            "FEEDBACK_FROM",
        )
    )


def deliver(payload: Feedback):
    letter = EmailMessage()
    letter["Subject"] = "Спестовник — Обратна връзка"
    letter["From"] = os.environ["FEEDBACK_FROM"]
    letter["To"] = RECIPIENT
    letter["Reply-To"] = payload.email
    letter.set_content(
        f"Име: {payload.name}\nТелефон: {payload.phone or '—'}\nЕл. поща: {payload.email}\n\n{payload.message}"
    )
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
    now = time.monotonic()
    # Global bounded quota for this single-instance preview; no spoofable IP headers.
    with _lock:
        while _attempts and _attempts[0] <= now - 600:
            _attempts.popleft()
        if len(_attempts) >= 5:
            raise HTTPException(429, "Please try later", headers={"Retry-After": "600"})
        _attempts.append(now)
    try:
        deliver(payload)
    except (OSError, ValueError, smtplib.SMTPException):
        raise HTTPException(503, "Feedback is temporarily unavailable") from None
    # SMTP acceptance is not proof of final mailbox delivery.
    return {"status": "accepted"}
