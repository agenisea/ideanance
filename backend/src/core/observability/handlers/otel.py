"""OpenTelemetry trace handler — maps events to OTEL spans."""

from __future__ import annotations

from typing import Any

import structlog

from core.observability.events import TraceEvent

log = structlog.get_logger()


class OtelTraceHandler:
    """Maps trace events to OpenTelemetry spans.

    Stub implementation — OTEL import is optional.
    Logs at debug level when OTEL is not installed.
    """

    def __init__(self) -> None:
        self._tracer: Any = None
        self._spans: dict[str, Any] = {}
        try:
            from opentelemetry import trace

            self._tracer = trace.get_tracer("ideanance")
        except ImportError:
            log.debug("otel.not_installed")

    @property
    def name(self) -> str:
        return "otel"

    async def handle(self, event: TraceEvent) -> None:
        if self._tracer is None:
            log.debug(
                "otel.skipped",
                trace_type=event.type,
                reason="tracer_not_available",
            )
            return

        try:
            from opentelemetry import trace

            match event.type:
                case "agent_start" | "pipeline_start":
                    span = self._tracer.start_span(
                        event.data.get(
                            "agent_id", event.type
                        )
                    )
                    self._spans[event.trace_id] = span
                case "agent_end" | "pipeline_end":
                    span = self._spans.pop(
                        event.trace_id, None
                    )
                    if span:
                        for k, v in event.data.items():
                            span.set_attribute(k, str(v))
                        span.end()
                case "llm_call":
                    with self._tracer.start_as_current_span(
                        "llm_call"
                    ) as span:
                        for k, v in event.data.items():
                            span.set_attribute(k, str(v))
                case "error":
                    span = self._spans.get(
                        event.trace_id
                    )
                    if span:
                        span.set_status(
                            trace.StatusCode.ERROR,
                            event.data.get("message", ""),
                        )
                case _:
                    log.debug(
                        "otel.unhandled_event",
                        trace_type=event.type,
                    )
        except Exception:
            log.warning(
                "otel.handler_error", exc_info=True
            )
