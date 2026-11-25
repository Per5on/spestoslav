"""Shared test setup."""

import pytest

from app.request_limits import request_limits


@pytest.fixture(autouse=True)
def fresh_request_limits():
    """The limiter is process-wide; start every test with empty counters."""
    request_limits.buckets.clear()
    request_limits.next_cleanup = 0
    yield
    request_limits.buckets.clear()
