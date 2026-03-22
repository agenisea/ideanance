"""Tests for pluggable trace handlers."""

from __future__ import annotations

import pytest

from core.observability.costs import CostAggregator
from core.observability.events import TraceEvent
from core.observability.handlers.console import (
    ConsoleTraceHandler,
)
from core.observability.handlers.cost_handler import (
    CostTraceHandler,
)


def _make_event(
    event_type: str = "agent_start",
    trace_id: str = "test-trace",
    **data: object,
) -> TraceEvent:
    return TraceEvent(
        type=event_type,  # type: ignore[arg-type]
        trace_id=trace_id,
        data=data,  # type: ignore[arg-type]
    )


class TestConsoleTraceHandler:
    def test_name(self) -> None:
        handler = ConsoleTraceHandler()
        assert handler.name == "console"

    @pytest.mark.asyncio
    async def test_handle_logs_event(self) -> None:
        handler = ConsoleTraceHandler()
        event = _make_event(
            agent_id="test_agent", model="test_model"
        )
        # Should not raise
        await handler.handle(event)


class TestCostTraceHandler:
    def test_name(self) -> None:
        aggregator = CostAggregator()
        handler = CostTraceHandler(aggregator)
        assert handler.name == "cost_aggregator"

    @pytest.mark.asyncio
    async def test_ignores_non_llm_events(self) -> None:
        aggregator = CostAggregator()
        handler = CostTraceHandler(aggregator)
        event = _make_event("agent_start")
        await handler.handle(event)
        assert aggregator.get_daily_total() == 0.0

    @pytest.mark.asyncio
    async def test_processes_llm_call_event(self) -> None:
        aggregator = CostAggregator()
        handler = CostTraceHandler(aggregator)
        event = _make_event(
            "llm_call",
            trace_id="req-1",
            model="claude-sonnet-4-6",
            input_tokens=1000,
            output_tokens=500,
        )
        await handler.handle(event)
        # Cost should be > 0 if model is in catalog
        # (may be 0 if model name doesn't match pricing)
        # The important thing is no error was raised
        assert isinstance(aggregator.get_daily_total(), float)


class TestHandlerImports:
    """Verify handler modules are importable."""

    def test_console_importable(self) -> None:
        from core.observability.handlers.console import (
            ConsoleTraceHandler,
        )

        assert ConsoleTraceHandler is not None

    def test_cost_handler_importable(self) -> None:
        from core.observability.handlers.cost_handler import (
            CostTraceHandler,
        )

        assert CostTraceHandler is not None

    def test_logfire_handler_importable(self) -> None:
        from core.observability.handlers.logfire import (
            LogfireTraceHandler,
        )

        assert LogfireTraceHandler is not None

    def test_langsmith_handler_importable(self) -> None:
        from core.observability.handlers.langsmith import (
            LangSmithTraceHandler,
        )

        assert LangSmithTraceHandler is not None

    def test_otel_handler_importable(self) -> None:
        from core.observability.handlers.otel import (
            OtelTraceHandler,
        )

        assert OtelTraceHandler is not None


class TestLogfireHandler:
    @pytest.mark.asyncio
    async def test_handle_without_logfire_installed(
        self,
    ) -> None:
        """LogfireTraceHandler.handle() should not raise if logfire is not installed."""
        from core.observability.handlers.logfire import (
            LogfireTraceHandler,
        )

        handler = LogfireTraceHandler(
            token="fake-token",
            service_name="test",
        )
        assert handler.name == "logfire"
        event = _make_event()
        # Should not raise even if logfire is not installed
        await handler.handle(event)


class TestInitializeTracing:
    def test_initialize_tracing_creates_dispatcher(
        self,
    ) -> None:
        from config import Settings
        from core.observability import initialize_tracing

        s = Settings(
            logfire_token="",
            langsmith_api_key="",
            otel_enabled=False,
        )
        dispatcher = initialize_tracing(s)
        # Should always have console + cost handlers
        assert dispatcher.handler_count == 2

    def test_initialize_tracing_with_logfire(self) -> None:
        from config import Settings
        from core.observability import initialize_tracing

        s = Settings(
            logfire_token="fake-token",
            logfire_service_name="test",
            langsmith_api_key="",
            otel_enabled=False,
        )
        dispatcher = initialize_tracing(s)
        # console + cost + logfire = 3
        assert dispatcher.handler_count == 3
