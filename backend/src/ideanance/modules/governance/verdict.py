"""GovernanceVerdict — final governance evaluation result."""

from __future__ import annotations

from dataclasses import dataclass, field

from ideanance.modules.governance.constants import (
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_WARN,
)
from ideanance.modules.governance.evidence import Evidence


@dataclass
class LensFinding:
    """A single finding from a lens evaluation."""

    lens: str
    status: str  # STATUS_PASS | STATUS_WARN | STATUS_FAIL
    policy_id: str
    message: str
    evidence: list[Evidence] = field(
        default_factory=list
    )
    confidence: float = 1.0


@dataclass
class LensResult:
    """All findings from one lens."""

    lens: str
    findings: list[LensFinding] = field(
        default_factory=list
    )
    confidence: float = 1.0
    status: str = STATUS_PASS

    def __post_init__(self) -> None:
        if self.findings:
            self.confidence = min(
                f.confidence for f in self.findings
            )
            statuses = {f.status for f in self.findings}
            if STATUS_FAIL in statuses:
                self.status = STATUS_FAIL
            elif STATUS_WARN in statuses:
                self.status = STATUS_WARN


@dataclass
class GovernanceVerdict:
    """Final governance evaluation result."""

    state: str  # VERDICT_PROCEED | VERDICT_ESCALATE | VERDICT_BLOCKED
    confidence: float
    lens_results: list[LensResult] = field(
        default_factory=list
    )
    finding_count: int = 0
