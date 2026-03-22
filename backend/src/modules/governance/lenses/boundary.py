"""BoundaryLens — scope, actions, stop conditions.

Detects PII leakage, credential exposure, out-of-scope advice
(medical, legal, financial), and frustration/escalation keywords.
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
from modules.governance.lenses.patterns import (
    CREDENTIAL_PATTERNS,
    PII_PATTERNS,
)
from modules.governance.verdict import (
    LensFinding,
    LensResult,
)

if TYPE_CHECKING:
    from modules.governance.engine import GovernanceEngine
    from modules.governance.loader import LoadedPolicy

# --- Keywords ---

FRUSTRATION_KEYWORDS: list[str] = [
    "this is broken",
    "not working",
    "useless",
    "frustrated",
    "give up",
    "waste of time",
    "terrible",
    "horrible",
    "worst",
]

LEGAL_KEYWORDS: list[str] = [
    "legal advice",
    "attorney",
    "lawsuit",
    "litigation",
    "liability",
    "sue",
    "court order",
    "legal opinion",
    "legal counsel",
]

MEDICAL_KEYWORDS: list[str] = [
    "diagnosis",
    "prescribe",
    "medication",
    "treatment plan",
    "medical advice",
    "dosage",
    "symptoms indicate",
    "prognosis",
    "clinical recommendation",
]

FINANCIAL_ADVICE_KEYWORDS: list[str] = [
    "invest in",
    "buy stocks",
    "financial advice",
    "guaranteed returns",
    "portfolio allocation",
    "tax advice",
    "retirement plan",
    "hedge fund",
    "trading strategy",
]

# Pattern for advice-giving language
_ADVICE_PATTERN = re.compile(
    r"\b(?:you should|i recommend|i advise|"
    r"my recommendation is|you must|you need to)\b",
    re.IGNORECASE,
)


def check_pii(content: str) -> list[tuple[str, str]]:
    """Check content for PII using shared patterns."""
    hits: list[tuple[str, str]] = []
    for label, pat in PII_PATTERNS:
        for match in pat.finditer(content):
            hits.append((label, match.group()))
    return hits


def check_secrets(content: str) -> list[tuple[str, str]]:
    """Check content for credential exposure."""
    hits: list[tuple[str, str]] = []
    for label, pat in CREDENTIAL_PATTERNS:
        for match in pat.finditer(content):
            hits.append((label, match.group()))
    return hits


def check_keywords(
    content: str, keywords: list[str]
) -> list[str]:
    """Generic keyword matcher. Returns matched keywords."""
    lower = content.lower()
    return [kw for kw in keywords if kw in lower]


def contains_medical_advice(content: str) -> list[str]:
    """Detect medical advice: keywords + advice-giving pattern."""
    hits = check_keywords(content, MEDICAL_KEYWORDS)
    if hits and _ADVICE_PATTERN.search(content):
        return hits
    return []


def contains_legal_advice(content: str) -> list[str]:
    """Detect legal advice: keywords + advice-giving pattern."""
    hits = check_keywords(content, LEGAL_KEYWORDS)
    if hits and _ADVICE_PATTERN.search(content):
        return hits
    return []


def contains_financial_advice(content: str) -> list[str]:
    """Detect financial advice: keywords + advice-giving pattern."""
    hits = check_keywords(content, FINANCIAL_ADVICE_KEYWORDS)
    if hits and _ADVICE_PATTERN.search(content):
        return hits
    return []


class BoundaryLens:
    """Evaluates scope, risk management, stop conditions.

    Detection order (strict dominance):
    1. PII detected -> BLOCKED
    2. Secrets detected -> BLOCKED
    3. Medical/legal/financial advice -> BLOCKED
    4. Frustration keywords -> ESCALATE
    5. Engine rule evaluation -> per-rule status
    """

    def __init__(
        self,
        engine: GovernanceEngine | None = None,
    ) -> None:
        self._engine = engine

    @property
    def name(self) -> str:
        return "boundary"

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

        # 1. PII check -> BLOCKED
        pii_hits = check_pii(content)
        if pii_hits:
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.BLOCKED,
                    policy_id="boundary-pii",
                    message=(
                        f"PII detected: {', '.join(h[0] for h in pii_hits)}"
                    ),
                    evidence=[
                        Evidence(
                            claim=f"PII type '{t}' found",
                            source="artifact",
                            pointer="design",
                            excerpt=v[:40],
                        )
                        for t, v in pii_hits
                    ],
                    confidence=self._calculate_confidence(
                        len(pii_hits)
                    ),
                )
            )
            # Strict dominance: return early on BLOCKED
            return LensResult(
                lens=self.name, findings=findings
            )

        # 2. Secrets check -> BLOCKED
        secret_hits = check_secrets(content)
        if secret_hits:
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.BLOCKED,
                    policy_id="boundary-secrets",
                    message=(
                        f"Credentials detected: "
                        f"{', '.join(h[0] for h in secret_hits)}"
                    ),
                    evidence=[
                        Evidence(
                            claim=f"Credential type '{t}'",
                            source="artifact",
                            pointer="design",
                            excerpt=v[:20] + "...",
                        )
                        for t, v in secret_hits
                    ],
                    confidence=self._calculate_confidence(
                        len(secret_hits)
                    ),
                )
            )
            return LensResult(
                lens=self.name, findings=findings
            )

        # 3. Scope checks (medical/legal/financial) -> BLOCKED
        for label, detector in (
            ("medical", contains_medical_advice),
            ("legal", contains_legal_advice),
            ("financial", contains_financial_advice),
        ):
            hits = detector(content)
            if hits:
                findings.append(
                    LensFinding(
                        lens=self.name,
                        status=GovernanceState.BLOCKED,
                        policy_id=f"boundary-{label}-advice",
                        message=(
                            f"Out-of-scope {label} advice detected"
                        ),
                        evidence=[
                            Evidence(
                                claim=f"{label} keyword: {kw}",
                                source="artifact",
                                pointer="design",
                            )
                            for kw in hits
                        ],
                        confidence=self._calculate_confidence(
                            len(hits)
                        ),
                    )
                )
                return LensResult(
                    lens=self.name, findings=findings
                )

        # 4. Escalation keywords -> ESCALATE
        frustration = check_keywords(
            content, FRUSTRATION_KEYWORDS
        )
        if frustration:
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.ESCALATE,
                    policy_id="boundary-frustration",
                    message=(
                        "Frustration/escalation keywords detected"
                    ),
                    evidence=[
                        Evidence(
                            claim=f"Keyword: {kw}",
                            source="artifact",
                            pointer="design",
                        )
                        for kw in frustration
                    ],
                    confidence=self._calculate_confidence(
                        len(frustration),
                        uncertain=True,
                    ),
                )
            )

        # 5. Delegate to engine for policy rule evaluation
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
