"""Native session bridge to the existing managed identity provider.

Only the provider's signed session cookie is returned, never a service key.
Native clients store it in OS secure storage and exchange it for short-lived JWTs.
"""

import os
import re

import httpx
from fastapi import APIRouter, Header, HTTPException, Response
from pydantic import BaseModel, Field
from .auth import auth_base_url

router = APIRouter(prefix="/api/v1/auth")
COOKIE = "__Secure-neon-auth.session_token"


class Credentials(BaseModel):
    email: str = Field(
        min_length=3, max_length=254, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    )
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(default="Спестовник", min_length=1, max_length=100)


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
        if result.status_code != 200:
            code = (
                result.status_code
                if result.status_code in (400, 401, 403, 409, 429)
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


@router.post("/sign-in")
def sign_in(payload: Credentials, response: Response):
    data, cookie = upstream(
        "/sign-in/email",
        "POST",
        payload={"email": payload.email, "password": payload.password},
    )
    return session_result(data, cookie, response)


@router.post("/sign-up")
def sign_up(payload: Credentials, response: Response):
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
