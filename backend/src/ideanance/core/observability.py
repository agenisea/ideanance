"""Logfire observability setup."""

from __future__ import annotations

from typing import Any

from ideanance.config import settings


def configure_observability(app: Any) -> None:
    """Initialize Logfire if token is configured."""
    if not settings.logfire_token:
        return

    import logfire

    logfire.configure(
        token=settings.logfire_token,
        service_name=settings.logfire_service_name,
    )
    logfire.instrument_pydantic_ai()
    logfire.instrument_fastapi(app)
