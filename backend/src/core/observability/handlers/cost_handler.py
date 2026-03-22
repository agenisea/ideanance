"""Cost trace handler — wraps existing CostAggregator."""

from __future__ import annotations

from core.observability.costs import (
    CostAggregator,
    TokenUsage,
)
from core.observability.events import TraceEvent


class CostTraceHandler:
    """Wraps CostAggregator as a pluggable trace handler.

    Only processes llm_call events — all others are ignored.
    """

    def __init__(self, aggregator: CostAggregator) -> None:
        self._aggregator = aggregator

    @property
    def name(self) -> str:
        return "cost_aggregator"

    async def handle(self, event: TraceEvent) -> None:
        if event.type != "llm_call":
            return
        usage = TokenUsage(
            prompt_tokens=int(
                event.data.get("input_tokens", 0)
            ),
            completion_tokens=int(
                event.data.get("output_tokens", 0)
            ),
            model=str(event.data.get("model", "")),
        )
        self._aggregator.add_usage(event.trace_id, usage)
