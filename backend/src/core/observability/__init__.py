"""Deep observability: cost tracking, PII sanitization, North Star metrics.

Exports the core tracing infrastructure:
- TraceDispatcher: fan-out to registered handlers
- TraceEvent: typed immutable event dataclass
- TraceHandler: pluggable handler protocol
- initialize_tracing: create dispatcher + register handlers from config
- configure_observability: legacy Logfire-only setup (kept for compat)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import structlog

from core.observability.dispatcher import TraceDispatcher
from core.observability.events import TraceEvent
from core.observability.protocols import TraceHandler

if TYPE_CHECKING:
    from config import Settings

log = structlog.get_logger()

__all__ = [
    "TraceDispatcher",
    "TraceEvent",
    "TraceHandler",
    "configure_observability",
    "initialize_tracing",
]


def configure_observability(app: Any) -> None:
    """Initialize Logfire if token is configured.

    Legacy function — prefer initialize_tracing() for the
    full pluggable dispatcher pipeline.
    """
    from config import settings

    if not settings.logfire_token:
        return

    try:
        import logfire

        logfire.configure(
            token=settings.logfire_token,
            service_name=settings.logfire_service_name,
        )
        logfire.instrument_pydantic_ai()
        logfire.instrument_fastapi(app)
    except ImportError:
        log.warning("logfire.not_installed")


def initialize_tracing(settings: Settings) -> TraceDispatcher:
    """Create dispatcher and register handlers based on config."""
    from core.observability.costs import CostAggregator
    from core.observability.handlers.console import (
        ConsoleTraceHandler,
    )
    from core.observability.handlers.cost_handler import (
        CostTraceHandler,
    )

    dispatcher = TraceDispatcher()

    # Always register console + cost
    dispatcher.register(ConsoleTraceHandler())
    dispatcher.register(
        CostTraceHandler(CostAggregator())
    )

    # Logfire (pydantic-ai native)
    if settings.logfire_token:
        from core.observability.handlers.logfire import (
            LogfireTraceHandler,
        )

        dispatcher.register(
            LogfireTraceHandler(
                token=settings.logfire_token,
                service_name=settings.logfire_service_name,
            )
        )

    # LangSmith (lazy import)
    if settings.langsmith_api_key:
        try:
            from core.observability.handlers.langsmith import (
                LangSmithTraceHandler,
            )

            dispatcher.register(
                LangSmithTraceHandler(
                    api_key=settings.langsmith_api_key,
                    project=settings.langsmith_project,
                )
            )
        except ImportError:
            log.warning("langsmith_unavailable")

    # OpenTelemetry
    if settings.otel_enabled:
        try:
            from core.observability.handlers.otel import (
                OtelTraceHandler,
            )

            dispatcher.register(OtelTraceHandler())
        except ImportError:
            log.warning("otel_unavailable")

    import contextlib

    with contextlib.suppress(Exception):
        log.info(
            "tracing.initialized",
            handler_count=dispatcher.handler_count,
        )
    return dispatcher
