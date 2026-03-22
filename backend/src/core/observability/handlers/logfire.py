"""Logfire trace handler — pydantic-ai native instrumentation."""

from __future__ import annotations

from typing import Any

import structlog

from core.observability.events import TraceEvent

log = structlog.get_logger()


def configure_logfire(
    app: Any, token: str, service_name: str
) -> None:
    """One-time Logfire setup — instruments FastAPI + pydantic-ai.

    Called by TraceDispatcher.configure_integrations(), not by
    the handler directly.
    """
    try:
        import logfire

        logfire.configure(
            token=token, service_name=service_name
        )
        logfire.instrument_pydantic_ai()
        logfire.instrument_fastapi(app)
        log.info(
            "logfire.configured",
            service_name=service_name,
        )
    except ImportError:
        log.warning("logfire.not_installed")
    except Exception:
        log.warning("logfire.configure_failed", exc_info=True)


class LogfireTraceHandler:
    """Pydantic-AI native tracing via Logfire.

    Split from configure_logfire() for SRP:
    - configure_logfire() handles one-time app setup
    - This class handles per-event tracing
    """

    def __init__(
        self, token: str, service_name: str
    ) -> None:
        self._token = token
        self._service_name = service_name

    @property
    def name(self) -> str:
        return "logfire"

    def configure_app(self, app: Any) -> None:
        """Delegated from TraceDispatcher.configure_integrations()."""
        configure_logfire(
            app, self._token, self._service_name
        )

    async def handle(self, event: TraceEvent) -> None:
        try:
            import logfire

            logfire.info(
                "{trace_type}",
                trace_type=event.type,
                trace_id=event.trace_id,
                category=event.category,
                **event.data,
            )
        except ImportError:
            pass
