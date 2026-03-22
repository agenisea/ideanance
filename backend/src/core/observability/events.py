"""Typed trace events for the observability pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

TraceEventType = Literal[
    "agent_start",
    "agent_end",
    "pipeline_start",
    "pipeline_end",
    "governance_eval_start",
    "governance_eval_end",
    "llm_call",
    "tool_call",
    "handoff",
    "fallback",
    "error",
]

TraceCategory = Literal[
    "agent",
    "pipeline",
    "governance",
    "llm",
    "export",
]


@dataclass(frozen=True)
class TraceEvent:
    """Immutable trace event emitted through the dispatcher."""

    type: TraceEventType
    trace_id: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
    category: TraceCategory = "agent"
    data: dict[str, Any] = field(default_factory=dict)
