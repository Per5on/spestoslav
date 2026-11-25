"""Bound short-lived request counters for a single API process."""

import hashlib
import ipaddress
import math
import os
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request


class RequestLimits:
    def __init__(self, *, clock=monotonic, capacity=20_000):
        self.clock = clock
        self.capacity = capacity
        self.buckets = {}
        self.lock = Lock()
        self.next_cleanup = 0

    def check(self, scope, seconds, *limits):
        with self.lock:
            now = self.clock()
            if now >= self.next_cleanup:
                self.buckets = {
                    key: bucket for key, bucket in self.buckets.items() if bucket[0] > now
                }
                self.next_cleanup = now + 60
            changes = {}
            for identity, maximum in limits:
                key = (scope, hashlib.sha256(identity.encode()).digest())
                expires, count = self.buckets.get(key, (now, 0))
                if expires <= now:
                    expires, count = now + seconds, 0
                if count >= maximum:
                    self.reject(math.ceil(expires - now))
                changes[key] = (expires, count + 1)
            if len(self.buckets) + sum(key not in self.buckets for key in changes) > self.capacity:
                self.reject(max(1, math.ceil(self.next_cleanup - now)))
            self.buckets.update(changes)

    @staticmethod
    def reject(after):
        raise HTTPException(429, "Please wait before retrying", headers={"Retry-After": str(after)})


request_limits = RequestLimits()


def trusted_proxy_hops():
    """Number of reverse proxies in front of the API that append to X-Forwarded-For.

    Defaults to 0 (use the socket peer). On a host such as Render, set
    TRUSTED_PROXY_HOPS to the number of proxies you trust so each person gets their
    own rate-limit bucket instead of all sharing the proxy's address.
    """
    try:
        return max(0, min(int(os.getenv("TRUSTED_PROXY_HOPS", "0")), 5))
    except ValueError:
        return 0


def client_address(request: Request):
    peer = request.client.host if request.client else "unknown"
    hops = trusted_proxy_hops()
    if hops:
        chain = [
            part.strip()
            for part in request.headers.get("x-forwarded-for", "").split(",")
            if part.strip()
        ]
        # Entries are appended on the right by each proxy, so the address seen by the
        # outermost trusted proxy is hops-from-the-right. Anything a client prepends
        # sits to the left of it and is ignored.
        if len(chain) >= hops:
            try:
                return str(ipaddress.ip_address(chain[-hops]))
            except ValueError:
                pass
    return peer


def limit_locality_search(request: Request):
    request_limits.check("locality", 60, (client_address(request), 120))
