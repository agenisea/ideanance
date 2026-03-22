"""Cost aggregation — track token costs per request, agent, and day."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import structlog

log = structlog.get_logger()

COST_CONFIG: dict[str, dict[str, float]] = {
    "claude-sonnet-4-6": {
        "prompt_per_1k": 0.003,
        "completion_per_1k": 0.015,
    },
    "claude-haiku-4-5": {
        "prompt_per_1k": 0.001,
        "completion_per_1k": 0.005,
    },
    "claude-opus-4-6": {
        "prompt_per_1k": 0.005,
        "completion_per_1k": 0.025,
    },
    "gpt-4o": {
        "prompt_per_1k": 0.0025,
        "completion_per_1k": 0.01,
    },
    "text-embedding-3-small": {
        "prompt_per_1k": 0.00002,
        "completion_per_1k": 0.0,
    },
}

DAILY_COST_LIMIT = 10.0
MONTHLY_COST_LIMIT = 145.0


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    model: str


def calculate_cost(usage: TokenUsage) -> float:
    config = COST_CONFIG.get(usage.model)
    if config is None:
        return 0.0
    return (usage.prompt_tokens / 1000) * config[
        "prompt_per_1k"
    ] + (usage.completion_tokens / 1000) * config["completion_per_1k"]


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
