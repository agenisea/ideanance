"""Protocol for handoff management — enables DIP and testability."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ideanance.core.handoff.schema import HandoffRequest, HandoffResponse


@runtime_checkable
class HandoffManagerProtocol(Protocol):
    """Manages agent-to-agent delegation with safety guards."""

    async def process_handoff(
        self, request: HandoffRequest
    ) -> HandoffResponse: ...

    def reset(self) -> None: ...
