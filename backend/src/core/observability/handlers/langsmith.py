"""LangSmith trace handler — lazy import, run hierarchy mapping."""

from __future__ import annotations

from typing import Any

import structlog

from core.observability.events import TraceEvent

log = structlog.get_logger()


class LangSmithTraceHandler:
    """Maps trace events to LangSmith run hierarchy.

    Uses lazy import so langsmith is never a hard dependency.
    """

    def __init__(
        self,
        api_key: str,
        project: str = "ideanance",
    ) -> None:
        self._client: Any = None
        self._api_key = api_key
        self._project = project

    @property
    def name(self) -> str:
        return "langsmith"

    def _ensure_client(self) -> Any:
        if self._client is None:
            from langsmith import Client

            self._client = Client(api_key=self._api_key)
        return self._client

    async def handle(self, event: TraceEvent) -> None:
        try:
            client = self._ensure_client()
            match event.type:
                case "agent_start":
                    client.create_run(
                        name=event.data.get(
                            "agent_id", "agent"
                        ),
                        run_type="chain",
                        project_name=self._project,
                        inputs=event.data,
                    )
                case "agent_end":
                    log.debug(
                        "langsmith.agent_end",
                        trace_id=event.trace_id,
                    )
                case "llm_call":
                    log.debug(
                        "langsmith.llm_call",
                        trace_id=event.trace_id,
                        model=event.data.get("model"),
                    )
                case _:
                    log.debug(
                        "langsmith.event",
                        trace_type=event.type,
                        trace_id=event.trace_id,
                    )
        except ImportError:
            log.debug("langsmith.not_installed")
        except Exception:
            log.warning(
                "langsmith.handler_error",
                exc_info=True,
            )
