"""5-level fallback chain: Primary -> Simplified -> Template -> Cache -> Honest Error.

Immutable axiom from NORTHSTAR_EXTRACT.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

import structlog

from ideanance.core.resilience.honest_error import HonestError

log = structlog.get_logger()


@dataclass
class FallbackLevel:
    name: str
    execute: Callable[[], Coroutine[Any, Any, Any]]
    timeout_s: float


@dataclass
class FallbackResult:
    result: Any
    level: int
    level_name: str


class FallbackChain:
    """Executes levels in order until one succeeds."""

    def __init__(
        self,
        levels: list[FallbackLevel],
        final_fallback: HonestError,
    ) -> None:
        self.levels = levels
        self.final_fallback = final_fallback

    async def execute(self) -> FallbackResult:
        for i, level in enumerate(self.levels):
            try:
                result = await asyncio.wait_for(
                    level.execute(), timeout=level.timeout_s
                )
                if result is not None:
                    log.info(
                        "fallback.resolved",
                        level=i,
                        level_name=level.name,
                    )
                    return FallbackResult(
                        result=result, level=i, level_name=level.name
                    )
            except (TimeoutError, Exception) as e:
                log.warning(
                    "fallback.level_failed",
                    level=i,
                    level_name=level.name,
                    error=str(e),
                )
                continue

        log.warning("fallback.exhausted")
        self.final_fallback.fallback_levels_attempted = len(self.levels)
        return FallbackResult(
            result=self.final_fallback,
            level=len(self.levels),
            level_name="honest_error",
        )
