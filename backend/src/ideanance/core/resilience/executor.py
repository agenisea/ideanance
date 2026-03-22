"""ResilientExecutor: integrates circuit breaker + retry + fallback chain."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

import structlog

from ideanance.core.resilience.circuit_breaker import CircuitBreaker
from ideanance.core.resilience.fallback_chain import FallbackChain, FallbackResult

log = structlog.get_logger()


class ResilientExecutor:
    """Layer 1: Circuit breaker → Layer 2: Execute → Layer 3: Fallback."""

    def __init__(
        self,
        circuit_breaker: CircuitBreaker,
        fallback_chain: FallbackChain,
    ) -> None:
        self.cb = circuit_breaker
        self.fallback = fallback_chain

    async def execute(
        self,
        fn: Callable[[], Coroutine[Any, Any, Any]],
    ) -> FallbackResult:
        """Execute with circuit breaker protection and fallback."""
        # Layer 1: Circuit breaker check
        if not self.cb.can_execute():
            log.warning(
                "resilient.circuit_open",
                state=self.cb.state,
            )
            return await self.fallback.execute()

        # Layer 2: Try the primary function
        try:
            result = await fn()
            self.cb.on_success()
            return FallbackResult(
                result=result, level=0, level_name="primary"
            )
        except Exception as e:
            self.cb.on_failure()
            log.warning(
                "resilient.primary_failed",
                error=str(e),
                circuit_state=self.cb.state,
            )
            # Layer 3: Fallback chain
            return await self.fallback.execute()
