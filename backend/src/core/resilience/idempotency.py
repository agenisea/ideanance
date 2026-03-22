"""Idempotency for governance checks and exports."""

from __future__ import annotations

import hashlib
from typing import Any


def generate_idempotency_key(
    workspace_id: str,
    agent_id: str,
    content_hash: str,
) -> str:
    """Generate a deterministic idempotency key."""
    raw = f"{workspace_id}:{agent_id}:{content_hash}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def hash_content(data: Any) -> str:
    """Hash arbitrary data for idempotency key generation."""
    import json

    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


class IdempotencyStore:
    """In-memory idempotency store. Replace with Redis in production."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def clear(self) -> None:
        self._store.clear()
