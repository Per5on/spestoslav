"""Shared fixtures: in-process rate-limit state must not leak between tests."""

import pytest


@pytest.fixture(autouse=True)
def fresh_rate_limits():
    from app import feedback, mobile_auth

    for window in (feedback._attempts, mobile_auth._per_email, mobile_auth._total):
        window.clear()
    yield
