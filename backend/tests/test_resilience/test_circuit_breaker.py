"""Tests for circuit breaker."""

from ideanance.core.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
)


def test_starts_closed():
    cb = CircuitBreaker(CircuitBreakerConfig())
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True


def test_opens_after_threshold_failures():
    cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3))
    cb.on_failure()
    cb.on_failure()
    assert cb.state == CircuitState.CLOSED
    cb.on_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False


def test_success_resets_failure_count():
    cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3))
    cb.on_failure()
    cb.on_failure()
    cb.on_success()
    assert cb.failure_count == 0
    assert cb.state == CircuitState.CLOSED


def test_half_open_after_timeout():
    cb = CircuitBreaker(
        CircuitBreakerConfig(failure_threshold=1, timeout_s=0.0)
    )
    cb.on_failure()
    assert cb.state == CircuitState.OPEN
    # timeout_s=0 means it immediately transitions to HALF_OPEN
    assert cb.can_execute() is True
    assert cb.state == CircuitState.HALF_OPEN


def test_half_open_closes_after_successes():
    cb = CircuitBreaker(
        CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=2,
            timeout_s=0.0,
        )
    )
    cb.on_failure()
    assert cb.state == CircuitState.OPEN
    cb.can_execute()  # triggers HALF_OPEN
    assert cb.state == CircuitState.HALF_OPEN

    cb.on_success()
    assert cb.state == CircuitState.HALF_OPEN  # need 2
    cb.on_success()
    assert cb.state == CircuitState.CLOSED
