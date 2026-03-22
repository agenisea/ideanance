"""SSE streaming helpers for agent output with error boundary."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any


async def stream_agent_response(
    agent: Any, prompt: str, deps: Any
) -> AsyncIterator[dict[str, str]]:
    """Stream agent response as SSE-compatible event dicts.

    Error boundary: emits honest_error event instead of silent drop.
    """
    try:
        async with agent.run_stream(prompt, deps=deps) as result:
            async for text in result.stream_text(delta=True):
                yield {
                    "event": "token",
                    "data": json.dumps({"text": text}),
                }

            final = await result.get_data()
            yield {
                "event": "result",
                "data": final.model_dump_json(),
            }
    except Exception as e:
        yield {
            "event": "honest_error",
            "data": json.dumps(
                {
                    "type": "honest_error",
                    "message": str(e),
                    "governance_status": "unknown",
                }
            ),
        }

    yield {"event": "done", "data": ""}
