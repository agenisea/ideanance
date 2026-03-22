"""Protocols for observability — enables DIP and testability."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ideanance.core.observability.costs import TokenUsage


@runtime_checkable
class CostAggregatorProtocol(Protocol):
    """Tracks token costs per request and daily totals."""

    def add_usage(
        self, request_id: str, usage: TokenUsage
    ) -> float: ...

    def is_over_daily_limit(self) -> bool: ...


@runtime_checkable
class KillSwitchProtocol(Protocol):
    """Manages global and per-agent kill switches."""

    def is_agent_enabled(self, agent_id: str) -> bool: ...

    def disable_all_agents(self, reason: str) -> None: ...

    def disable_agent(
        self, agent_id: str, reason: str
    ) -> None: ...
