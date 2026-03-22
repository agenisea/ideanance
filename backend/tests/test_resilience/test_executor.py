"""Tests for ResilientExecutor integration."""

from ideanance.core.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
)
from ideanance.core.resilience.executor import ResilientExecutor
from ideanance.core.resilience.fallback_chain import (
    FallbackChain,
    FallbackLevel,
)
from ideanance.core.resilience.honest_error import HonestError


async def test_executor_succeeds_on_primary():
    cb = CircuitBreaker(CircuitBreakerConfig())
    chain = FallbackChain(
        levels=[],
        final_fallback=HonestError(
            message="fail", governance_status="unknown"
        ),
    )
    executor = ResilientExecutor(cb, chain)

    async def primary():
        return "success"

    result = await executor.execute(primary)
    assert result.level_name == "primary"
    assert result.result == "success"


async def test_executor_uses_fallback_on_failure():
    cb = CircuitBreaker(CircuitBreakerConfig())
    chain = FallbackChain(
        levels=[
            FallbackLevel(
                name="template",
                execute=lambda: _async_return("template"),
                timeout_s=1.0,
            ),
        ],
        final_fallback=HonestError(
            message="fail", governance_status="unknown"
        ),
    )
    executor = ResilientExecutor(cb, chain)

    async def failing():
        raise RuntimeError("boom")

    result = await executor.execute(failing)
    assert result.level_name == "template"


async def test_executor_rejects_when_circuit_open():
    cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=1))
    cb.on_failure()  # Open the circuit

    chain = FallbackChain(
        levels=[],
        final_fallback=HonestError(
            message="circuit open",
            governance_status="unknown",
        ),
    )
    executor = ResilientExecutor(cb, chain)

    async def should_not_run():
        raise AssertionError("Should not be called")

    result = await executor.execute(should_not_run)
    assert result.level_name == "honest_error"


async def _async_return(value: str) -> str:
    return value
