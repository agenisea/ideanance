"""In-process event bus using asyncio.Queue per workspace subscriber."""

from __future__ import annotations

import asyncio
import contextlib
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

# Domain event types (published by services)
EVENT_POLICY_CREATED = "governance.policy.created"
EVENT_WIRING_CREATED = "governance.wiring.created"
EVENT_FRAMEWORK_ACTIVATED = "governance.framework.activated"
EVENT_EXPORT_COMPLETED = "export.completed"

# Reserved — defined for future wiring
EVENT_DESIGN_UPDATED = "design.updated"  # Reserved
EVENT_GOVERNANCE_CHECK_COMPLETED = "governance.check.completed"  # Reserved
EVENT_FRAMEWORK_SEEDED = "governance.framework.seeded"  # Reserved
EVENT_CONFLICTS_DETECTED = "governance.conflicts.detected"  # Reserved
EVENT_TOPOLOGY_EVALUATED = "agents.topology.evaluated"  # Reserved
EVENT_EVAL_THRESHOLD_BREACHED = "evaluation.threshold.breached"  # Reserved

# Backpressure: max events queued per subscriber
EVENT_QUEUE_MAX_SIZE = 1000


@dataclass
class Event:
    type: str
    payload: dict[str, Any]
    workspace_id: str
    id: str = field(default_factory=lambda: str(uuid4()))


class EventBus:
    """In-process event bus with per-workspace fan-out.

    Supports global listeners for cross-cutting observers
    (e.g., NorthStarTracker) that need all events.
    """

    def __init__(self) -> None:
        self._subscribers: dict[
            str, list[asyncio.Queue[Event]]
        ] = {}
        self._global_listeners: list[
            Callable[[Event], None]
        ] = []
        self._lock = threading.Lock()

    def subscribe(
        self, workspace_id: str
    ) -> asyncio.Queue[Event]:
        with self._lock:
            queue: asyncio.Queue[Event] = asyncio.Queue(
                maxsize=EVENT_QUEUE_MAX_SIZE
            )
            self._subscribers.setdefault(
                workspace_id, []
            ).append(queue)
            return queue

    def unsubscribe(
        self,
        workspace_id: str,
        queue: asyncio.Queue[Event],
    ) -> None:
        with self._lock:
            if workspace_id in self._subscribers:
                self._subscribers[workspace_id].remove(
                    queue
                )
                if not self._subscribers[workspace_id]:
                    del self._subscribers[workspace_id]

    def add_global_listener(
        self, listener: Callable[[Event], None]
    ) -> None:
        """Register a listener that receives ALL events."""
        self._global_listeners.append(listener)

    async def publish(self, event: Event) -> None:
        # Global listeners first (sync — for NorthStar, etc.)
        for listener in self._global_listeners:
            listener(event)
        # Per-workspace subscribers
        for queue in self._subscribers.get(
            event.workspace_id, []
        ):
            with contextlib.suppress(asyncio.QueueFull):
                queue.put_nowait(event)
