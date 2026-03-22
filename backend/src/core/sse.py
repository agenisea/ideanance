"""SSE broadcaster for per-workspace event fan-out.

Provides a singleton EventBus instance. Full SSE endpoint implementation
is in api/v1/events.py (PLAN5).
"""

from __future__ import annotations

from core.events import EventBus

_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
