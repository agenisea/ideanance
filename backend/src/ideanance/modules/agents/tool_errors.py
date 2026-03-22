"""Cross-cutting error handler for agent tools.

Structured error handling for agent tools.
"""

from __future__ import annotations

import functools
from typing import Any

import structlog

log = structlog.get_logger()


def handle_tool_errors(func):  # type: ignore[no-untyped-def]
    """Decorator for pydantic-ai tool functions.

    Catches exceptions and returns safe error messages
    instead of crashing the agent run.
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            log.warning(
                "tool.known_error",
                tool=func.__name__,
                error=str(e),
            )
            return f"Error: {e}"
        except Exception as e:
            log.error(
                "tool.unexpected_error",
                tool=func.__name__,
                error=str(e),
            )
            return (
                "An internal error occurred. "
                "Please try rephrasing your request."
            )

    return wrapper
