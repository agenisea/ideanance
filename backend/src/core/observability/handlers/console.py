"""Console trace handler — logs via structlog."""

from __future__ import annotations

import structlog

from core.observability.events import TraceEvent

log = structlog.get_logger()


class ConsoleTraceHandler:
    """Logs trace events as structlog key=value messages."""

    @property
    def name(self) -> str:
        return "console"

    async def handle(self, event: TraceEvent) -> None:
        log.info(
            "trace",
            trace_type=event.type,
            trace_id=event.trace_id,
            category=event.category,
            **event.data,
        )
