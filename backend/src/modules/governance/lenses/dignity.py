"""DignityLens — non-discrimination, fairness, empowerment.

Detects dismissive language, high-pressure tactics, exclusionary
patterns, and validates the presence of human escalation paths
and empathy.
"""

from __future__ import annotations

import re
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

# --- Dignity detection patterns ---

_I = re.IGNORECASE

DISMISSIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\b(?:just|simply)\s+(?:deal with it"
        r"|get over it|move on)\b",
        _I,
    ),
    re.compile(
        r"\bthat(?:'s| is)\s+(?:not (?:my|our)"
        r" (?:problem|concern)|irrelevant)\b",
        _I,
    ),
    re.compile(
        r"\b(?:you(?:'re| are)\s+(?:wrong"
        r"|overreacting|being difficult))\b",
        _I,
    ),
    re.compile(
        r"\b(?:doesn(?:'t| not) matter"
        r"|who cares|so what)\b",
        _I,
    ),
    re.compile(
        r"\b(?:too bad|tough luck"
        r"|not my problem)\b",
        _I,
    ),
]

PRESSURE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\b(?:act now|limited time"
        r"|last chance|urgent)\b",
        _I,
    ),
    re.compile(
        r"\b(?:you must|you have to"
        r"|no choice|mandatory)\b",
        _I,
    ),
    re.compile(
        r"\b(?:don(?:'t| not) miss|hurry"
        r"|expires? (?:soon|today))\b",
        _I,
    ),
    re.compile(
        r"\b(?:final offer|now or never"
        r"|one-time)\b",
        _I,
    ),
    re.compile(
        r"\b(?:failure to (?:comply|act)"
        r"|consequences)\b",
        _I,
    ),
]

EXCLUSION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\b(?:not (?:for|intended for"
        r"|designed for) (?:you|people like))\b",
        _I,
    ),
    re.compile(
        r"\b(?:only (?:for|available to)"
        r" (?:certain|select|qualified))\b",
        _I,
    ),
    re.compile(
        r"\b(?:you (?:don(?:'t| not)"
        r"|wouldn(?:'t| not)) understand)\b",
        _I,
    ),
    re.compile(
        r"\b(?:this is(?:n't| not) for"
        r" (?:beginners|novices|laypeople))\b",
        _I,
    ),
]

HUMAN_ESCALATION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\b(?:speak (?:to|with) (?:a |an )?"
        r"(?:human|person|representative"
        r"|agent))\b",
        _I,
    ),
    re.compile(
        r"\b(?:human (?:review|oversight"
        r"|agent|support))\b",
        _I,
    ),
    re.compile(
        r"\b(?:escalat(?:e|ion)"
        r"|transfer to)\b",
        _I,
    ),
    re.compile(
        r"\b(?:contact (?:support|us|help))\b",
        _I,
    ),
]

EMPATHY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\b(?:i understand|i hear you"
        r"|that(?:'s| is) (?:understandable"
        r"|valid|a fair point))\b",
        _I,
    ),
    re.compile(
        r"\b(?:i(?:'m| am) sorry"
        r"|apolog(?:y|ize|ies))\b",
        _I,
    ),
    re.compile(
        r"\b(?:thank you for|i appreciate)\b",
        _I,
    ),
    re.compile(
        r"\b(?:that must be|i can see how)\b",
        _I,
    ),
]


def check_dismissive(content: str) -> list[str]:
    """Detect dismissive language."""
    hits: list[str] = []
    for pat in DISMISSIVE_PATTERNS:
        m = pat.search(content)
        if m:
            hits.append(m.group())
    return hits


def check_pressure(content: str) -> list[str]:
    """Detect high-pressure tactics."""
    hits: list[str] = []
    for pat in PRESSURE_PATTERNS:
        m = pat.search(content)
        if m:
            hits.append(m.group())
    return hits


def check_exclusion(content: str) -> list[str]:
    """Detect exclusionary patterns."""
    hits: list[str] = []
    for pat in EXCLUSION_PATTERNS:
        m = pat.search(content)
        if m:
            hits.append(m.group())
    return hits


def has_human_escalation(content: str) -> list[str]:
    """Check for human escalation path."""
    hits: list[str] = []
    for pat in HUMAN_ESCALATION_PATTERNS:
        m = pat.search(content)
        if m:
            hits.append(m.group())
    return hits


def has_empathy(content: str) -> list[str]:
    """Check for empathetic language."""
    hits: list[str] = []
    for pat in EMPATHY_PATTERNS:
        m = pat.search(content)
        if m:
            hits.append(m.group())
    return hits


class DignityLens:
    """Evaluates non-discrimination, fairness, empowerment.

    Detection order (strict dominance):
    1. Dismissive language -> BLOCKED
    2. Pressure without escalation -> BLOCKED
    3. Pressure with escalation -> ESCALATE
    4. Missing escalation path -> ESCALATE
    5. Exclusion -> ESCALATE
    6. Engine rule evaluation -> per-rule status
    """

    def __init__(
        self,
        engine: GovernanceEngine | None = None,
    ) -> None:
        self._engine = engine

    @property
    def name(self) -> str:
        return "dignity"

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
        content = str(artifact.get("design", artifact))
        findings: list[LensFinding] = []

        # 1. Dismissive language -> BLOCKED
        dismissive = check_dismissive(content)
        if dismissive:
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.BLOCKED,
                    policy_id="dignity-dismissive",
                    message="Dismissive language detected",
                    evidence=[
                        Evidence(
                            claim=f"Dismissive: {d}",
                            source="artifact",
                            pointer="design",
                        )
                        for d in dismissive
                    ],
                    confidence=self._calculate_confidence(
                        len(dismissive)
                    ),
                )
            )
            return LensResult(
                lens=self.name, findings=findings
            )

        # 2-3. Pressure tactics
        pressure = check_pressure(content)
        escalation = has_human_escalation(content)
        if pressure and not escalation:
            # Pressure without escalation -> BLOCKED
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.BLOCKED,
                    policy_id="dignity-pressure-no-escalation",
                    message=(
                        "Pressure tactics without "
                        "human escalation path"
                    ),
                    evidence=[
                        Evidence(
                            claim=f"Pressure: {p}",
                            source="artifact",
                            pointer="design",
                        )
                        for p in pressure
                    ],
                    confidence=self._calculate_confidence(
                        len(pressure)
                    ),
                )
            )
            return LensResult(
                lens=self.name, findings=findings
            )
        elif pressure and escalation:
            # Pressure with escalation -> ESCALATE
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.ESCALATE,
                    policy_id="dignity-pressure-with-escalation",
                    message=(
                        "Pressure tactics present but "
                        "escalation path available"
                    ),
                    evidence=[
                        Evidence(
                            claim=f"Pressure: {p}",
                            source="artifact",
                            pointer="design",
                        )
                        for p in pressure
                    ]
                    + [
                        Evidence(
                            claim=f"Escalation: {e}",
                            source="artifact",
                            pointer="design",
                        )
                        for e in escalation
                    ],
                    confidence=self._calculate_confidence(
                        len(pressure) + len(escalation),
                        uncertain=True,
                    ),
                )
            )

        # 4. Missing escalation path -> ESCALATE
        if not escalation and not pressure:
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.ESCALATE,
                    policy_id="dignity-no-escalation",
                    message=(
                        "No human escalation path found"
                    ),
                    evidence=[],
                    confidence=self._calculate_confidence(
                        0, uncertain=True
                    ),
                )
            )

        # 5. Exclusion -> ESCALATE
        exclusion = check_exclusion(content)
        if exclusion:
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.ESCALATE,
                    policy_id="dignity-exclusion",
                    message="Exclusionary language detected",
                    evidence=[
                        Evidence(
                            claim=f"Exclusion: {e}",
                            source="artifact",
                            pointer="design",
                        )
                        for e in exclusion
                    ],
                    confidence=self._calculate_confidence(
                        len(exclusion), uncertain=True
                    ),
                )
            )

        # 6. Delegate to engine for policy rule evaluation
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
