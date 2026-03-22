"""Cost aggregation — track token costs per request, agent, and day."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import structlog

from core.model_catalog import MODEL_PRICING

log = structlog.get_logger()

DAILY_COST_LIMIT = 10.0
MONTHLY_COST_LIMIT = 145.0


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    model: str


def _strip_provider(model: str) -> str:
    """Strip provider prefix if present.

    For example, 'anthropic:claude-sonnet-4-6' becomes
    'claude-sonnet-4-6'.
    """
    if ":" in model:
        return model.split(":", 1)[1]
    return model


def calculate_cost(usage: TokenUsage) -> float:
    """Calculate cost from token usage using the model catalog.

    Accepts both bare model names (e.g. 'claude-sonnet-4-6') and
    provider-prefixed names (e.g. 'anthropic:claude-sonnet-4-6').
    """
    pricing = MODEL_PRICING.get(usage.model)
    if pricing is None:
        # Try with provider prefix stripped for backward compat
        bare = _strip_provider(usage.model)
        # Search by bare name
        for key, p in MODEL_PRICING.items():
            if _strip_provider(key) == bare:
                pricing = p
                break
    if pricing is None:
        return 0.0
    return (usage.prompt_tokens / 1000) * pricing.prompt_per_1k + (
        usage.completion_tokens / 1000
    ) * pricing.completion_per_1k


class CostAggregator:
    """Tracks costs per request and daily totals."""

    def __init__(self) -> None:
        self._request_costs: dict[str, float] = defaultdict(float)
        self._daily_total: float = 0.0

    def add_usage(
        self, request_id: str, usage: TokenUsage
    ) -> float:
        cost = calculate_cost(usage)
        self._request_costs[request_id] += cost
        self._daily_total += cost

        if self._daily_total > DAILY_COST_LIMIT:
            log.warning(
                "cost.daily_limit_exceeded",
                daily_total=self._daily_total,
                limit=DAILY_COST_LIMIT,
            )

        return cost

    def get_daily_total(self) -> float:
        return self._daily_total

    def is_over_daily_limit(self) -> bool:
        return self._daily_total > DAILY_COST_LIMIT

    def reset_daily(self) -> None:
        self._daily_total = 0.0

    def clear_request(self, request_id: str) -> None:
        self._request_costs.pop(request_id, None)
