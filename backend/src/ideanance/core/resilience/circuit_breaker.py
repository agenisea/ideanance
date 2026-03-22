"""Per-agent circuit breaker: CLOSED -> OPEN -> HALF_OPEN."""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import StrEnum


class CircuitState(StrEnum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 3
    success_threshold: int = 2
    timeout_s: float = 20.0
    reset_s: float = 90.0


class CircuitBreaker:
    """Circuit breaker with configurable thresholds per agent."""

    def __init__(self, config: CircuitBreakerConfig) -> None:
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0

    def can_execute(self) -> bool:
        """Check if we should attempt the call."""
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.monotonic() - self.last_failure_time > self.config.timeout_s:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        # HALF_OPEN — allow one attempt
        return True

    def on_success(self) -> None:
        """Record a successful call."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0

    def on_failure(self) -> None:
        """Record a failed call."""
        self.last_failure_time = time.monotonic()
        self.failure_count += 1
        self.success_count = 0
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
