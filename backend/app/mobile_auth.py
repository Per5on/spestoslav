"""Native session bridge to the existing managed identity provider.

Only the provider's signed session cookie is returned, never a service key.
Native clients store it in OS secure storage and exchange it for short-lived JWTs.
"""

import os
import re

import httpx
from fastapi import APIRouter, Header, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator
from .auth import auth_base_url
from .request_limits import client_address, request_limits

router = APIRouter(prefix="/api/v1/auth")
COOKIE = "__Secure-neon-auth.session_token"


class RecoveryEmail(BaseModel):
    email: str = Field(
        min_length=3, max_length=254, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class Credentials(RecoveryEmail):
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(default="Спестовник", min_length=1, max_length=100)


class PasswordReset(RecoveryEmail):
    otp: str = Field(pattern=r"^[0-9]{6}$")
    password: str = Field(min_length=8, max_length=128)


def upstream(path, method="GET", session=None, payload=None):
    headers = {
        "Origin": os.getenv("AUTH_CLIENT_ORIGIN", "https://spestoslav-api.onrender.com")
    }
    if session:
        if len(session) > 2048 or not re.fullmatch(r"[A-Za-z0-9._%+=/-]+", session):
            raise HTTPException(401, "Invalid session")
        headers["Cookie"] = COOKIE + "=" + session
    try:
        result = httpx.request(
            method,
            auth_base_url() + path,
            headers=headers,
            json=payload,
            timeout=20,
            follow_redirects=False,
        )
        if result.status_code >= 500:
            raise HTTPException(503, "Sign-in service unavailable")
        if path.startswith("/email-otp/") and result.status_code == 204:
            return {}, None
        if result.status_code == 429:
            retry_after = result.headers.get("retry-after", "60")
            if not re.fullmatch(r"[0-9]{1,6}", retry_after):
                retry_after = "60"
            raise HTTPException(429, "Please wait before retrying", headers={"Retry-After": retry_after})
        if result.status_code != 200:
            if path == "/sign-up/email" and result.status_code == 422:
                try:
                    failure = result.json()
                except ValueError:
                    failure = None
                code = failure.get("code") if isinstance(failure, dict) else None
                if code == "USER_ALREADY_EXISTS_USE_ANOTHER_EMAIL":
                    raise HTTPException(409, "Account already exists")
                raise HTTPException(422, "Registration request was not accepted")
            if path.startswith("/email-otp/") and result.status_code in (404, 422):
                raise HTTPException(result.status_code, "Password reset request was not accepted")
            code = (
                result.status_code
                if result.status_code in (400, 401, 403, 409)
                else 502
            )
            raise HTTPException(code, "Sign-in request was not accepted")
        data = result.json()
        return data, result.cookies.get(COOKIE)
    except (httpx.RequestError, ValueError):
        raise HTTPException(503, "Sign-in service unavailable") from None


def session_result(data, cookie, response):
    response.headers["Cache-Control"] = "no-store"
    if not cookie:
        raise HTTPException(403, "Complete email verification before signing in")
    jwt, _ = upstream("/token", session=cookie)
    if not jwt.get("token"):
        raise HTTPException(502, "Identity provider returned no access token")
    user = data.get("user", {})
    return {
        "session": cookie,
        "access_token": jwt["token"],
        "user": {
            "id": user.get("id"),
            "email": user.get("email"),
            "name": user.get("name"),
        },
    }


def limit_auth(request, scope, email, per_email, per_address):
    request_limits.check(
        scope, 900, ("email:" + email, per_email), ("address:" + client_address(request), per_address)
    )


@router.post("/sign-in")
def sign_in(payload: Credentials, request: Request, response: Response):
    # Failed guesses are counted per email+address (10), so a stranger cannot lock a
    # victim out from elsewhere; a looser per-email cap (40) still slows distributed
    # guessing, and a per-address cap (60) slows one source trying many accounts.
    address = client_address(request)
    request_limits.check(
        "sign-in",
        900,
        ("pair:" + payload.email + "|" + address, 10),
        ("email:" + payload.email, 40),
        ("address:" + address, 60),
    )
    data, cookie = upstream(
        "/sign-in/email",
        "POST",
        payload={"email": payload.email, "password": payload.password},
    )
    return session_result(data, cookie, response)


@router.post("/sign-up")
def sign_up(payload: Credentials, request: Request, response: Response):
    # Each attempt can make the provider send a verification email.
    limit_auth(request, "sign-up", payload.email, 5, 20)
    data, cookie = upstream("/sign-up/email", "POST", payload=payload.model_dump())
    return session_result(data, cookie, response)


@router.post("/refresh")
def refresh(
    response: Response, x_auth_session: str = Header(min_length=1, max_length=2048)
):
    response.headers["Cache-Control"] = "no-store"
    data, _ = upstream("/get-session", session=x_auth_session)
    if not data or not data.get("user"):
        raise HTTPException(401, "Session expired")
    return session_result(data, x_auth_session, response)


@router.post("/sign-out")
def sign_out(
    response: Response, x_auth_session: str = Header(min_length=1, max_length=2048)
):
    response.headers["Cache-Control"] = "no-store"
    upstream("/sign-out", "POST", session=x_auth_session, payload={})
    return {"success": True}


@router.post("/request-password-reset", status_code=204)
def request_password_reset(payload: RecoveryEmail, request: Request, response: Response):
    limit_auth(request, "request-reset", payload.email, 3, 20)
    response.headers["Cache-Control"] = "no-store"
    try:
        upstream("/email-otp/request-password-reset", "POST", payload=payload.model_dump())
    except HTTPException as exc:
        # Keep the same public response for recognized and unrecognized addresses.
        if exc.status_code not in (400, 404, 422):
            raise


@router.post("/reset-password", status_code=204)
def reset_password(payload: PasswordReset, request: Request, response: Response):
    limit_auth(request, "verify-reset", payload.email, 5, 30)
    response.headers["Cache-Control"] = "no-store"
    try:
        upstream("/email-otp/reset-password", "POST", payload=payload.model_dump())
    except HTTPException as exc:
        if exc.status_code in (400, 401, 403, 404, 422):
            raise HTTPException(400, "Reset code was not accepted") from None
        raise
