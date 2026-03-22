"""HandoffManager: routing, limits, circular detection, human escalation."""

from __future__ import annotations

import time

import structlog

from core.handoff.constants import HandoffStatus
from core.handoff.limits import (
    CIRCULAR_DETECTION_WINDOW,
    MAX_HANDOFFS_PER_REQUEST,
)
from core.handoff.schema import HandoffRequest, HandoffResponse

log = structlog.get_logger()


class HandoffManager:
    """Manages agent-to-agent delegation with safety guards."""

    def __init__(self) -> None:
        self._handoff_counts: dict[str, int] = {}
        self._history: list[HandoffRequest] = []

    async def process_handoff(
        self, request: HandoffRequest
    ) -> HandoffResponse:
        """Process a handoff request with limits and circular detection."""
        start = time.monotonic()

        log.info(
            "handoff.request",
            trace_id=request.trace_id,
            source=request.source_agent,
            target=request.handoff_to,
            reason=request.reason,
        )

        # Check limits
        count = self._handoff_counts.get(request.trace_id, 0)
        if count >= MAX_HANDOFFS_PER_REQUEST:
            return self._failed_response(
                request, "Handoff limit exceeded", start
            )

        # Detect circular handoffs
        if self._detect_circular(request):
            return self._failed_response(
                request, "Circular handoff detected", start
            )

        # Handle human escalation
        if request.handoff_to == "human":
            return self._escalate_to_human(request, start)

        # Track
        self._handoff_counts[request.trace_id] = count + 1
        self._history.append(request)

        # Return a pending response — actual execution happens in pipeline
        elapsed_ms = (time.monotonic() - start) * 1000
        return HandoffResponse(
            trace_id=request.trace_id,
            responding_agent=request.handoff_to,
            status=HandoffStatus.RESOLVED,
            execution_time_ms=round(elapsed_ms, 1),
        )

    def _detect_circular(self, request: HandoffRequest) -> bool:
        """Check recent handoffs for same source->target->reason."""
        recent = self._history[-CIRCULAR_DETECTION_WINDOW:]
        same_path = sum(
            1
            for h in recent
            if h.source_agent == request.source_agent
            and h.handoff_to == request.handoff_to
            and h.reason == request.reason
        )
        return same_path >= 2

    def _escalate_to_human(
        self, request: HandoffRequest, start: float
    ) -> HandoffResponse:
        log.warning(
            "handoff.human_escalation",
            trace_id=request.trace_id,
            reason=request.reason_detail,
        )
        elapsed_ms = (time.monotonic() - start) * 1000
        return HandoffResponse(
            trace_id=request.trace_id,
            responding_agent="human",
            status=HandoffStatus.ESCALATED,
            execution_time_ms=round(elapsed_ms, 1),
        )

    def _failed_response(
        self, request: HandoffRequest, reason: str, start: float
    ) -> HandoffResponse:
        elapsed_ms = (time.monotonic() - start) * 1000
        return HandoffResponse(
            trace_id=request.trace_id,
            responding_agent="orchestrator",
            status=HandoffStatus.FAILED,
            failure_reason=reason,
            execution_time_ms=round(elapsed_ms, 1),
        )

    def reset(self) -> None:
        """Reset state between pipeline runs."""
        self._handoff_counts.clear()
        self._history.clear()
