"""Small in-process sliding-window limiter for the single-instance preview."""

import time
from collections import deque
from threading import Lock

from fastapi import HTTPException


class SlidingWindow:
    def __init__(self, limit, seconds):
        self.limit, self.seconds = limit, seconds
        self._hits, self._lock = {}, Lock()

    def hit(self, key=""):
        """Record one attempt for key or raise 429 when the window is full."""
        now = time.monotonic()
        with self._lock:
            if len(self._hits) > 10_000:  # drop idle keys; bounds memory
                self._hits = {
                    k: q for k, q in self._hits.items() if q[-1] > now - self.seconds
                }
            window = self._hits.setdefault(key, deque())
            while window and window[0] <= now - self.seconds:
                window.popleft()
            if len(window) >= self.limit:
                raise HTTPException(
                    429, "Please try later", headers={"Retry-After": str(self.seconds)}
                )
            window.append(now)

    def __len__(self):  # attempts currently recorded; lets tests assert "none"
        with self._lock:
            return sum(len(q) for q in self._hits.values())

    def clear(self):
        with self._lock:
            self._hits.clear()
