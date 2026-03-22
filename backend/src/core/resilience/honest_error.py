"""HonestError schema — returned when all fallback levels are exhausted."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel


class HonestError(BaseModel):
    """Structured error with governance status and retry guidance.

    Every honest error must include governance_status so the user
    never assumes compliance when the system has degraded.
    """

    type: Literal["honest_error"] = "honest_error"
    message: str
    governance_status: str  # "unknown" | "stale" | "incomplete"
    retry_after_seconds: int = 30
    suggested_action: str = "retry"  # "retry" | "manual_review" | "use_raw_data"
    fallback_levels_attempted: int = 0
    timestamp: str = ""

    def model_post_init(self, _context: object) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()
