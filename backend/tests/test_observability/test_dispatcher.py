"""Tests for TraceDispatcher — registration, fan-out, best-effort."""

from __future__ import annotations

import pytest

from core.observability.dispatcher import TraceDispatcher
from core.observability.events import TraceEvent


class FakeHandler:
    """Fake handler for testing."""

    def __init__(
        self, handler_name: str = "fake"
    ) -> None:
        self._name = handler_name
        self.events: list[TraceEvent] = []

    @property
    def name(self) -> str:
        return self._name

    async def handle(self, event: TraceEvent) -> None:
        self.events.append(event)


class BrokenHandler:
    """Handler that always raises."""

    @property
    def name(self) -> str:
        return "broken"

    async def handle(self, event: TraceEvent) -> None:
        raise RuntimeError("intentional test error")


class AppConfigHandler:
    """Handler with configure_app support."""

    def __init__(self) -> None:
        self.configured_app = None

    @property
    def name(self) -> str:
        return "app_config"

    async def handle(self, event: TraceEvent) -> None:
        pass

    def configure_app(self, app: object) -> None:
        self.configured_app = app


def _make_event(
    event_type: str = "agent_start",
    trace_id: str = "test-trace-001",
) -> TraceEvent:
    return TraceEvent(
        type=event_type,  # type: ignore[arg-type]
        trace_id=trace_id,
        data={"agent_id": "test_agent"},
    )


class TestTraceDispatcher:
    def test_register_handler(self) -> None:
        dispatcher = TraceDispatcher()
        handler = FakeHandler()
        dispatcher.register(handler)
        assert dispatcher.handler_count == 1

    def test_register_deduplicates_by_name(self) -> None:
        dispatcher = TraceDispatcher()
        dispatcher.register(FakeHandler("same"))
        dispatcher.register(FakeHandler("same"))
        assert dispatcher.handler_count == 1

    def test_register_different_names(self) -> None:
        dispatcher = TraceDispatcher()
        dispatcher.register(FakeHandler("a"))
        dispatcher.register(FakeHandler("b"))
        assert dispatcher.handler_count == 2

    @pytest.mark.asyncio
    async def test_emit_fans_out_to_all_handlers(
        self,
    ) -> None:
        dispatcher = TraceDispatcher()
        h1 = FakeHandler("h1")
        h2 = FakeHandler("h2")
        dispatcher.register(h1)
        dispatcher.register(h2)

        event = _make_event()
        await dispatcher.emit(event)

        assert len(h1.events) == 1
        assert len(h2.events) == 1
        assert h1.events[0] is event
        assert h2.events[0] is event

    @pytest.mark.asyncio
    async def test_emit_best_effort_continues_on_error(
        self,
    ) -> None:
        """Handler error should not prevent other handlers from receiving events."""
        dispatcher = TraceDispatcher()
        broken = BrokenHandler()
        healthy = FakeHandler("healthy")
        dispatcher.register(broken)
        dispatcher.register(healthy)

        event = _make_event()
        # Should not raise
        await dispatcher.emit(event)

        # Healthy handler still received the event
        assert len(healthy.events) == 1

    @pytest.mark.asyncio
    async def test_emit_no_handlers(self) -> None:
        """Emit with no handlers should be a no-op."""
        dispatcher = TraceDispatcher()
        await dispatcher.emit(_make_event())

    def test_handler_count_empty(self) -> None:
        dispatcher = TraceDispatcher()
        assert dispatcher.handler_count == 0

    def test_configure_integrations_delegates(
        self,
    ) -> None:
        dispatcher = TraceDispatcher()
        handler = AppConfigHandler()
        dispatcher.register(handler)

        sentinel = object()
        dispatcher.configure_integrations(sentinel)

        assert handler.configured_app is sentinel

    def test_configure_integrations_skips_handlers_without_configure_app(
        self,
    ) -> None:
        dispatcher = TraceDispatcher()
        dispatcher.register(FakeHandler())
        # Should not raise
        dispatcher.configure_integrations(object())
