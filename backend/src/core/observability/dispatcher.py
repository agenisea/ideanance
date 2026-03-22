"""Trace dispatcher — fan-out to registered handlers."""

from __future__ import annotations

from typing import Any

import structlog

from core.observability.events import TraceEvent
from core.observability.protocols import TraceHandler

log = structlog.get_logger()


class TraceDispatcher:
    """Fan-out dispatcher — emits events to all registered handlers.

    Best-effort delivery: handler errors are logged, never raised.
    """

    def __init__(self) -> None:
        self._handlers: list[TraceHandler] = []

    def register(self, handler: TraceHandler) -> None:
        """Register a handler, deduplicating by name."""
        if not any(h.name == handler.name for h in self._handlers):
            self._handlers.append(handler)

    async def emit(self, event: TraceEvent) -> None:
        """Emit an event to all registered handlers."""
        for handler in self._handlers:
            try:
                await handler.handle(event)
            except Exception:
                log.warning(
                    "trace_handler_error",
                    handler=handler.name,
                    event_type=event.type,
                    exc_info=True,
                )

    def configure_integrations(self, app: Any) -> None:
        """Delegate app-level setup to handlers that support it."""
        for handler in self._handlers:
            if hasattr(handler, "configure_app"):
                handler.configure_app(app)

    @property
    def handler_count(self) -> int:
        """Number of registered handlers."""
        return len(self._handlers)
