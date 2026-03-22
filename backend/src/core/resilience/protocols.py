"""Protocol for resilient execution — enables DIP and testability."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any, Protocol, runtime_checkable

from core.resilience.fallback_chain import FallbackResult


@runtime_checkable
class ResilientExecutorProtocol(Protocol):
    """Executes a function with circuit breaker + fallback chain."""

    async def execute(
        self,
        fn: Callable[[], Coroutine[Any, Any, Any]],
    ) -> FallbackResult: ...
