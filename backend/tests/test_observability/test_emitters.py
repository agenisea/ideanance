"""Tests for typed emitter convenience functions."""

from __future__ import annotations

import pytest

from core.observability.dispatcher import TraceDispatcher
from core.observability.emitters import (
    emit_agent_end,
    emit_agent_start,
    emit_error,
    emit_fallback,
    emit_governance_eval,
    emit_handoff,
    emit_llm_call,
    emit_pipeline_end,
    emit_pipeline_start,
)
from core.observability.events import TraceEvent


class CaptureHandler:
    """Captures events for test assertions."""

    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    @property
    def name(self) -> str:
        return "capture"

    async def handle(self, event: TraceEvent) -> None:
        self.events.append(event)


def _setup() -> tuple[TraceDispatcher, CaptureHandler]:
    dispatcher = TraceDispatcher()
    handler = CaptureHandler()
    dispatcher.register(handler)
    return dispatcher, handler


class TestEmitters:
    @pytest.mark.asyncio
    async def test_emit_agent_start(self) -> None:
        dispatcher, handler = _setup()
        await emit_agent_start(
            dispatcher,
            "trace-1",
            "design_advisor",
            "claude-sonnet-4-6",
        )
        assert len(handler.events) == 1
        event = handler.events[0]
        assert event.type == "agent_start"
        assert event.trace_id == "trace-1"
        assert event.category == "agent"
        assert event.data["agent_id"] == "design_advisor"
        assert event.data["model"] == "claude-sonnet-4-6"

    @pytest.mark.asyncio
    async def test_emit_agent_end(self) -> None:
        dispatcher, handler = _setup()
        await emit_agent_end(
            dispatcher,
            "trace-1",
            "design_advisor",
            150.5,
            True,
        )
        event = handler.events[0]
        assert event.type == "agent_end"
        assert event.data["duration_ms"] == 150.5
        assert event.data["success"] is True

    @pytest.mark.asyncio
    async def test_emit_pipeline_start(self) -> None:
        dispatcher, handler = _setup()
        await emit_pipeline_start(
            dispatcher,
            "trace-2",
            "ws-123",
            "How to add fairness?",
        )
        event = handler.events[0]
        assert event.type == "pipeline_start"
        assert event.category == "pipeline"
        assert event.data["workspace_id"] == "ws-123"
        assert event.data["query"] == "How to add fairness?"

    @pytest.mark.asyncio
    async def test_emit_pipeline_end(self) -> None:
        dispatcher, handler = _setup()
        await emit_pipeline_end(
            dispatcher, "trace-2", 500.0, True
        )
        event = handler.events[0]
        assert event.type == "pipeline_end"
        assert event.category == "pipeline"
        assert event.data["duration_ms"] == 500.0

    @pytest.mark.asyncio
    async def test_emit_governance_eval(self) -> None:
        dispatcher, handler = _setup()
        await emit_governance_eval(
            dispatcher,
            "trace-3",
            policy_count=5,
            lens_count=3,
            findings_count=12,
        )
        event = handler.events[0]
        assert event.type == "governance_eval_end"
        assert event.category == "governance"
        assert event.data["policy_count"] == 5
        assert event.data["lens_count"] == 3
        assert event.data["findings_count"] == 12

    @pytest.mark.asyncio
    async def test_emit_llm_call(self) -> None:
        dispatcher, handler = _setup()
        await emit_llm_call(
            dispatcher,
            "trace-4",
            model="claude-sonnet-4-6",
            input_tokens=1000,
            output_tokens=500,
            duration_ms=2500.0,
            cost=0.0075,
        )
        event = handler.events[0]
        assert event.type == "llm_call"
        assert event.category == "llm"
        assert event.data["model"] == "claude-sonnet-4-6"
        assert event.data["input_tokens"] == 1000
        assert event.data["output_tokens"] == 500
        assert event.data["cost"] == 0.0075

    @pytest.mark.asyncio
    async def test_emit_handoff(self) -> None:
        dispatcher, handler = _setup()
        await emit_handoff(
            dispatcher,
            "trace-5",
            "query_router",
            "design_advisor",
            "design question detected",
        )
        event = handler.events[0]
        assert event.type == "handoff"
        assert event.data["from_agent"] == "query_router"
        assert event.data["to_agent"] == "design_advisor"
        assert (
            event.data["reason"]
            == "design question detected"
        )

    @pytest.mark.asyncio
    async def test_emit_fallback(self) -> None:
        dispatcher, handler = _setup()
        await emit_fallback(
            dispatcher,
            "trace-6",
            "policy_interpreter",
            "simplified_prompt",
            "primary agent failed",
        )
        event = handler.events[0]
        assert event.type == "fallback"
        assert event.data["level"] == "simplified_prompt"

    @pytest.mark.asyncio
    async def test_emit_error(self) -> None:
        dispatcher, handler = _setup()
        await emit_error(
            dispatcher,
            "trace-7",
            "eval_generator",
            "timeout exceeded",
        )
        event = handler.events[0]
        assert event.type == "error"
        assert event.data["component"] == "eval_generator"
        assert event.data["message"] == "timeout exceeded"

    @pytest.mark.asyncio
    async def test_event_timestamps_are_utc(self) -> None:
        from datetime import UTC

        dispatcher, handler = _setup()
        await emit_agent_start(
            dispatcher, "trace-8", "test", "model"
        )
        event = handler.events[0]
        assert event.timestamp.tzinfo is UTC
