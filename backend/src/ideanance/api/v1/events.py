"""SSE streaming endpoint for workspace events."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from ideanance.core.sse import get_event_bus

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/stream/{workspace_id}")
async def stream_workspace_events(workspace_id: str) -> EventSourceResponse:
    """Subscribe to workspace events via SSE."""
    event_bus = get_event_bus()

    async def event_generator():  # type: ignore[no-untyped-def]
        queue = event_bus.subscribe(workspace_id)
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                    yield {
                        "event": event.type,
                        "data": json.dumps(event.payload),
                        "id": event.id,
                    }
                except TimeoutError:
                    yield {"event": "ping", "data": ""}
        finally:
            event_bus.unsubscribe(workspace_id, queue)

    return EventSourceResponse(
        event_generator(),
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
        },
    )
