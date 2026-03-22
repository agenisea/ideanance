"""Handoff failure recovery strategies."""

from __future__ import annotations

from dataclasses import dataclass

from ideanance.core.handoff.schema import HandoffResponse


@dataclass
class RecoveryAction:
    action: str  # "retry_different_target" | "proceed_partial" | "escalate"
    reason: str
    new_target: str | None = None


def determine_recovery(
    response: HandoffResponse,
    attempt_number: int,
) -> RecoveryAction:
    """Determine recovery strategy based on failure type and attempt."""
    if response.status == "partial":
        return RecoveryAction(
            action="proceed_partial",
            reason="Non-critical inputs missing, proceeding with "
            "honest degradation",
        )

    if (
        response.status == "failed"
        and response.responding_agent != "orchestrator"
    ):
        return RecoveryAction(
            action="retry_different_target",
            reason="Primary target failed, escalating to orchestrator",
            new_target="orchestrator",
        )

    if attempt_number >= 3:
        return RecoveryAction(
            action="escalate",
            reason="Cannot recover after exhausting fallback chain",
        )

    return RecoveryAction(
        action="escalate",
        reason="Handoff failed, human input required",
    )
