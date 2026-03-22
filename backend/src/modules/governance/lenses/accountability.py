"""AccountabilityLens — human oversight, audit, ownership.

Validates policy/contract structure, not agent output content.
Checks for answerable human, escalation paths, and
accountability rules within the governance framework.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from modules.governance.constants import (
    DEFAULT_CONFIDENCE,
    GovernanceState,
)
from modules.governance.evidence import Evidence
from modules.governance.lenses.base import (
    get_lens_names_for_policy,
)
from modules.governance.verdict import (
    LensFinding,
    LensResult,
)

if TYPE_CHECKING:
    from modules.governance.engine import GovernanceEngine
    from modules.governance.loader import LoadedPolicy

# Keys in artifact that indicate accountability structures
_ACCOUNTABILITY_FIELDS = [
    "accountability",
    "human_oversight",
    "oversight",
]
_ANSWERABLE_HUMAN_FIELDS = [
    "answerable_human",
    "responsible_person",
    "owner",
    "human_oversight_measures",
]
_ESCALATION_FIELDS = [
    "escalation_path",
    "escalation",
    "escalation_procedure",
    "incident_response",
]


def _resolve_nested(
    data: dict[str, Any], keys: list[str]
) -> Any:
    """Look for any of the given keys in the artifact or nested dicts."""
    for key in keys:
        if key in data:
            return data[key]
    # Check nested under 'design'
    design = data.get("design", {})
    if isinstance(design, dict):
        for key in keys:
            if key in design:
                return design[key]
    # Check nested under accountability sub-dict
    for field in _ACCOUNTABILITY_FIELDS:
        acct = data.get(field) or (
            design.get(field) if isinstance(design, dict) else None
        )
        if isinstance(acct, dict):
            for key in keys:
                if key in acct:
                    return acct[key]
    return None


def validate_answerable_human(
    artifact: dict[str, Any],
) -> str | None:
    """Check if artifact has an answerable human defined.

    Returns the value if found, None otherwise.
    """
    value = _resolve_nested(
        artifact, _ANSWERABLE_HUMAN_FIELDS
    )
    if value and str(value).strip():
        return str(value)
    return None


def validate_escalation_path(
    artifact: dict[str, Any],
) -> str | None:
    """Check if artifact has an escalation path defined.

    Returns the value if found, None otherwise.
    """
    value = _resolve_nested(
        artifact, _ESCALATION_FIELDS
    )
    if value and str(value).strip():
        return str(value)
    return None


class AccountabilityLens:
    """Evaluates human oversight, audit, record-keeping.

    Validates policy/contract structure:
    1. Missing answerable human -> BLOCKED
    2. Missing escalation path -> ESCALATE
    3. Engine rule evaluation -> per-rule status
    """

    def __init__(
        self,
        engine: GovernanceEngine | None = None,
    ) -> None:
        self._engine = engine

    @property
    def name(self) -> str:
        return "accountability"

    def _get_engine(self) -> GovernanceEngine:
        if self._engine is None:
            from modules.governance.engine import (
                GovernanceEngine,
            )

            self._engine = GovernanceEngine()
        return self._engine

    def _calculate_confidence(
        self,
        evidence_count: int,
        *,
        uncertain: bool = False,
    ) -> float:
        """Calculate confidence with penalties.

        Penalties:
        - satisfied, no evidence: -0.05
        - satisfied, 1 evidence: -0.02
        - uncertain: -0.15
        """
        conf = DEFAULT_CONFIDENCE
        if uncertain:
            conf -= 0.15
        elif evidence_count == 0:
            conf -= 0.05
        elif evidence_count == 1:
            conf -= 0.02
        return max(0.0, round(conf, 2))

    def evaluate(
        self,
        artifact: dict[str, Any],
        policies: list[LoadedPolicy],
    ) -> LensResult:
        findings: list[LensFinding] = []

        # 1. Answerable human check -> BLOCKED if missing
        human = validate_answerable_human(artifact)
        if human is None:
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.BLOCKED,
                    policy_id="accountability-answerable-human",
                    message=(
                        "No answerable human defined — "
                        "accountability requires a named "
                        "responsible person"
                    ),
                    evidence=[],
                    confidence=self._calculate_confidence(
                        0
                    ),
                )
            )
        else:
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.PASS,
                    policy_id="accountability-answerable-human",
                    message=(
                        f"Answerable human: {human[:80]}"
                    ),
                    evidence=[
                        Evidence(
                            claim="Answerable human defined",
                            source="artifact",
                            pointer="accountability.answerable_human",
                            excerpt=human[:60],
                        )
                    ],
                    confidence=self._calculate_confidence(
                        1
                    ),
                )
            )

        # 2. Escalation path check -> ESCALATE if missing
        escalation = validate_escalation_path(artifact)
        if escalation is None:
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.ESCALATE,
                    policy_id="accountability-escalation-path",
                    message=(
                        "No escalation path defined — "
                        "incidents need a clear route "
                        "to human oversight"
                    ),
                    evidence=[],
                    confidence=self._calculate_confidence(
                        0, uncertain=True
                    ),
                )
            )
        else:
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.PASS,
                    policy_id="accountability-escalation-path",
                    message=(
                        f"Escalation path: {escalation[:80]}"
                    ),
                    evidence=[
                        Evidence(
                            claim="Escalation path defined",
                            source="artifact",
                            pointer="accountability.escalation_path",
                            excerpt=escalation[:60],
                        )
                    ],
                    confidence=self._calculate_confidence(
                        1
                    ),
                )
            )

        # 3. Delegate to engine for policy rule evaluation
        engine = self._get_engine()
        for policy in policies:
            if self.name not in get_lens_names_for_policy(
                policy
            ):
                continue
            results = engine.evaluate(
                artifact, policy.rules
            )
            for cr in results:
                findings.append(
                    LensFinding(
                        lens=self.name,
                        status=cr.status,
                        policy_id=policy.id,
                        message=cr.message,
                        evidence=[
                            Evidence(
                                claim=cr.message,
                                source="policy",
                                pointer=policy.id,
                            )
                        ],
                        confidence=self._calculate_confidence(
                            1
                        ),
                    )
                )

        return LensResult(
            lens=self.name, findings=findings
        )
