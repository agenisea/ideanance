"""GovernanceSynthesizer — strict state dominance.

BLOCKED > ESCALATE > PROCEED. Non-configurable policy.
Non-configurable policy, not tuning.
"""

from __future__ import annotations

from modules.governance.constants import (
    STATUS_FAIL,
    STATUS_WARN,
    VERDICT_BLOCKED,
    VERDICT_ESCALATE,
    VERDICT_PROCEED,
)
from modules.governance.verdict import (
    GovernanceVerdict,
    LensResult,
)

# Below this confidence, auto-escalate (honesty rule)
LOW_CONFIDENCE_THRESHOLD = 0.4


class GovernanceSynthesizer:
    """Strict state dominance: BLOCKED > ESCALATE > PROCEED."""

    def synthesize(
        self, lens_results: list[LensResult]
    ) -> GovernanceVerdict:
        all_findings = [
            f for r in lens_results for f in r.findings
        ]

        confidences = [
            r.confidence for r in lens_results
        ]
        confidence = (
            min(confidences) if confidences else 1.0
        )

        if any(
            f.status == STATUS_FAIL
            for f in all_findings
        ):
            state = VERDICT_BLOCKED
        elif (
            any(
                f.status == STATUS_WARN
                for f in all_findings
            )
            or confidence < LOW_CONFIDENCE_THRESHOLD
        ):
            state = VERDICT_ESCALATE
        else:
            state = VERDICT_PROCEED

        return GovernanceVerdict(
            state=state,
            confidence=confidence,
            lens_results=lens_results,
            finding_count=len(all_findings),
        )
