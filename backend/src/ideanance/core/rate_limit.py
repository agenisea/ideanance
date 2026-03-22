"""Simple in-memory rate limiter for agent endpoints."""

from __future__ import annotations

import time
from collections import defaultdict


class RateLimiter:
    """In-memory rate limiter. Sufficient for single-instance MVP.

    Construct in lifespan, expose via Depends(get_rate_limiter).
    """

    def __init__(
        self,
        max_requests: int = 30,
        window_seconds: int = 60,
    ) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> bool:
        """Return True if request is allowed, False if rate limited."""
        now = time.monotonic()
        self._requests[key] = [
            t
            for t in self._requests[key]
            if now - t < self.window
        ]
        if len(self._requests[key]) >= self.max_requests:
            return False
        self._requests[key].append(now)
        return True
