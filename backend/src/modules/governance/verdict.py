"""GovernanceVerdict — final governance evaluation result."""

from __future__ import annotations

from dataclasses import dataclass, field

from modules.governance.constants import GovernanceState
from modules.governance.evidence import Evidence


@dataclass
class LensFinding:
    """A single finding from a lens evaluation."""

    lens: str
    status: str  # GovernanceState.PASS | ESCALATE | BLOCKED
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
    status: str = GovernanceState.PASS

    def __post_init__(self) -> None:
        if self.findings:
            self.confidence = min(
                f.confidence for f in self.findings
            )
            statuses = {f.status for f in self.findings}
            if GovernanceState.BLOCKED in statuses:
                self.status = GovernanceState.BLOCKED
            elif GovernanceState.ESCALATE in statuses:
                self.status = GovernanceState.ESCALATE


@dataclass
class GovernanceVerdict:
    """Final governance evaluation result."""

    state: str  # GovernanceState.PROCEED | ESCALATE | BLOCKED
    confidence: float
    lens_results: list[LensResult] = field(
        default_factory=list
    )
    finding_count: int = 0
