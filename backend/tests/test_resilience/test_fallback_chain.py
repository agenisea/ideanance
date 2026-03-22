"""Tests for 5-level fallback chain."""

from core.resilience.fallback_chain import (
    FallbackChain,
    FallbackLevel,
)
from core.resilience.honest_error import HonestError


async def test_resolves_at_primary():
    chain = FallbackChain(
        levels=[
            FallbackLevel(
                name="primary",
                execute=lambda: _async_return("primary result"),
                timeout_s=1.0,
            ),
        ],
        final_fallback=_honest_error(),
    )
    result = await chain.execute()
    assert result.level == 0
    assert result.level_name == "primary"
    assert result.result == "primary result"


async def test_falls_to_second_level():
    chain = FallbackChain(
        levels=[
            FallbackLevel(
                name="primary",
                execute=lambda: _async_raise(),
                timeout_s=1.0,
            ),
            FallbackLevel(
                name="simplified",
                execute=lambda: _async_return("simplified result"),
                timeout_s=1.0,
            ),
        ],
        final_fallback=_honest_error(),
    )
    result = await chain.execute()
    assert result.level == 1
    assert result.level_name == "simplified"


async def test_exhausted_returns_honest_error():
    chain = FallbackChain(
        levels=[
            FallbackLevel(
                name="primary",
                execute=lambda: _async_raise(),
                timeout_s=1.0,
            ),
            FallbackLevel(
                name="simplified",
                execute=lambda: _async_raise(),
                timeout_s=1.0,
            ),
        ],
        final_fallback=_honest_error(),
    )
    result = await chain.execute()
    assert result.level_name == "honest_error"
    assert isinstance(result.result, HonestError)
    assert result.result.governance_status == "unknown"
    assert result.result.fallback_levels_attempted == 2


async def test_timeout_triggers_next_level():
    import asyncio

    async def slow_fn():
        await asyncio.sleep(10)
        return "never"

    chain = FallbackChain(
        levels=[
            FallbackLevel(
                name="slow",
                execute=slow_fn,
                timeout_s=0.01,
            ),
            FallbackLevel(
                name="fast",
                execute=lambda: _async_return("fast result"),
                timeout_s=1.0,
            ),
        ],
        final_fallback=_honest_error(),
    )
    result = await chain.execute()
    assert result.level_name == "fast"


# --- Helpers ---


async def _async_return(value: str) -> str:
    return value


async def _async_raise() -> str:
    raise RuntimeError("fail")


def _honest_error() -> HonestError:
    return HonestError(
        message="All levels exhausted.",
        governance_status="unknown",
    )
