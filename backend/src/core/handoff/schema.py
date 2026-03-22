"""Handoff schemas: HandoffRequest, HandoffResponse, MissingInput."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

HANDOFF_SCHEMA_VERSION = "1.0.0"


class MissingInput(BaseModel):
    key: str
    expected_type: str = "string"
    description: str = ""


class HandoffRequest(BaseModel):
    schema_version: str = HANDOFF_SCHEMA_VERSION
    trace_id: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    source_agent: str
    can_handle: bool = False
    handoff_to: str
    reason: str
    reason_detail: str = ""
    missing_inputs: list[MissingInput] | None = None
    context_for_target: dict = Field(default_factory=dict)
    priority: str = "medium"
    timeout_ms: int | None = None


class HandoffResponse(BaseModel):
    schema_version: str = HANDOFF_SCHEMA_VERSION
    trace_id: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    responding_agent: str
    status: str  # "resolved" | "partial" | "failed" | "escalated"
    provided_inputs: dict | None = None
    unresolved: list[str] | None = None
    failure_reason: str | None = None
    execution_time_ms: float = 0.0
