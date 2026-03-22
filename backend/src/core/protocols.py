"""Core protocols — cross-cutting infrastructure interfaces."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class RateLimiterProtocol(Protocol):
    """Rate limits requests by key."""

    def check(self, key: str) -> bool: ...
