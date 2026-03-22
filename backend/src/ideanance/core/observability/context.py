"""Request-scoped context via contextvars."""

from __future__ import annotations

import contextvars
import time
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True)
class RequestContext:
    request_id: str = field(default_factory=lambda: str(uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    workspace_id: str | None = None
    project_id: str | None = None
    session_id: str | None = None
    start_time_ns: int = field(default_factory=time.monotonic_ns)


_request_ctx: contextvars.ContextVar[RequestContext | None] = (
    contextvars.ContextVar("request_ctx", default=None)
)


def set_context(
    ctx: RequestContext,
) -> contextvars.Token[RequestContext | None]:
    return _request_ctx.set(ctx)


def get_context() -> RequestContext | None:
    return _request_ctx.get()


def get_request_id() -> str:
    ctx = get_context()
    return ctx.request_id if ctx else "unknown"
