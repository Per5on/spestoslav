"""Managed Neon JWT authentication and separate server-only service credentials."""

import hmac
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from urllib.parse import urlsplit

import jwt
from jwt import PyJWKClient
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)
_audience_warned = False


@dataclass(frozen=True)
class Principal:
    subject: str
    role: str = "user"


def auth_base_url():
    value = os.getenv("NEON_AUTH_BASE_URL", "").rstrip("/")
    if not value or urlsplit(value).scheme != "https":
        raise HTTPException(503, "Managed authentication is not configured")
    return value


@lru_cache(maxsize=4)
def jwks_client(url):
    return PyJWKClient(url, cache_keys=True, lifespan=300, timeout=5)


def _warn_missing_audience():
    global _audience_warned
    if not _audience_warned:
        _audience_warned = True
        logger.warning(
            "AUTH_AUDIENCE is not set: any token from the issuer is accepted. "
            "Set it and AUTH_REQUIRE_AUDIENCE=true in production."
        )


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            401, "Authentication required", headers={"WWW-Authenticate": "Bearer"}
        )
    base = auth_base_url()
    issuer = "{0.scheme}://{0.netloc}".format(urlsplit(base))
    jwks_url = os.getenv("NEON_AUTH_JWKS_URL", base + "/.well-known/jwks.json")
    try:
        key = jwks_client(jwks_url).get_signing_key_from_jwt(credentials.credentials)
        audience = os.getenv("AUTH_AUDIENCE")
        if not audience:
            if os.getenv("AUTH_REQUIRE_AUDIENCE", "").lower() == "true":
                raise HTTPException(503, "Authentication audience is not configured")
            _warn_missing_audience()
        claims = jwt.decode(
            credentials.credentials,
            key.key,
            algorithms=["EdDSA"],
            issuer=issuer,
            audience=audience,
            options={
                "require": ["exp", "iat", "iss", "sub"],
                "verify_aud": bool(audience),
            },
        )
        subject = claims["sub"]
        if not isinstance(subject, str) or not subject or len(subject) > 200:
            raise jwt.InvalidTokenError("Invalid subject")
    except jwt.PyJWKClientConnectionError:
        raise HTTPException(503, "Authentication provider is unavailable") from None
    except jwt.PyJWTError:
        raise HTTPException(
            401, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"}
        ) from None
    admins = {
        s.strip() for s in os.getenv("ADMIN_SUBJECTS", "").split(",") if s.strip()
    }
    return Principal(subject, "admin" if subject in admins else "user")


def service_key(config_name, supplied):
    expected = os.getenv(config_name, "")
    if len(expected) < 32:
        raise HTTPException(503, "Service authentication is not configured")
    if not supplied or not hmac.compare_digest(supplied.encode(), expected.encode()):
        raise HTTPException(401, "Invalid service credential")


def admin_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    x_admin_key: str | None = Header(default=None),
):
    if x_admin_key is not None:
        service_key("ADMIN_API_KEY", x_admin_key)
        return Principal("service:admin", "admin")
    user = current_user(credentials)
    if user.role != "admin":
        raise HTTPException(403, "Administrator access required")
    return user


def collector_user(x_collector_key: str | None = Header(default=None)):
    service_key("COLLECTOR_API_KEY", x_collector_key)
    return Principal("service:collector", "collector")
