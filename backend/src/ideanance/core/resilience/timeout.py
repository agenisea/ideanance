"""Timeout handling with TTFT enforcement for streaming agents."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any


async def with_timeout(
    fn: Callable[[], Coroutine[Any, Any, Any]],
    timeout_s: float,
    fallback: Any = None,
) -> Any:
    """Execute fn with timeout. Returns fallback on timeout."""
    try:
        return await asyncio.wait_for(fn(), timeout=timeout_s)
    except TimeoutError:
        return fallback
