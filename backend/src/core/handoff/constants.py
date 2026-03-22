"""Handoff domain constants."""

from enum import StrEnum


class HandoffStatus(StrEnum):
    RESOLVED = "resolved"
    PARTIAL = "partial"
    FAILED = "failed"
    ESCALATED = "escalated"
