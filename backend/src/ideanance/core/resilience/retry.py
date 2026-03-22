"""Retry strategies with exponential backoff and jitter.

Uses tenacity for retry logic.
"""

from __future__ import annotations

from dataclasses import dataclass

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)


@dataclass
class RetryConfig:
    max_retries: int = 3
    initial_wait_s: float = 0.1
    max_wait_s: float = 1.0
    jitter: bool = True


def build_retry_decorator(config: RetryConfig):  # type: ignore[no-untyped-def]
    """Build a tenacity retry decorator from config."""
    return retry(
        stop=stop_after_attempt(config.max_retries + 1),
        wait=wait_exponential_jitter(
            initial=config.initial_wait_s,
            max=config.max_wait_s,
            jitter=config.initial_wait_s if config.jitter else 0,
        ),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )


# Pre-built configs per component (from RESILIENCE_PATTERNS.md §5.1)
RETRY_CONFIGS = {
    "query_router": RetryConfig(
        max_retries=2, initial_wait_s=0.1, max_wait_s=0.5
    ),
    "domain_agent": RetryConfig(
        max_retries=1, initial_wait_s=0.2, max_wait_s=0.2, jitter=False
    ),
    "governance_filter": RetryConfig(
        max_retries=3, initial_wait_s=0.05, max_wait_s=0.2, jitter=False
    ),
    "export_formatter": RetryConfig(max_retries=0),
    "database": RetryConfig(
        max_retries=3, initial_wait_s=0.1, max_wait_s=1.0
    ),
    "embedding_api": RetryConfig(
        max_retries=2, initial_wait_s=0.2, max_wait_s=2.0
    ),
}
