"""PrivacyLens — data minimization, PII, consent, restraint.

Detects PII exposure, credential leakage, scope creep, and
excess data collection patterns.
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

# --- Privacy-specific patterns (beyond shared) ---

ADDRESS_PATTERN = re.compile(
    r"\b\d{1,5}\s+\w+\s+(?:st|street|ave|avenue|blvd|"
    r"boulevard|dr|drive|rd|road|ln|lane|ct|court)\b",
    re.IGNORECASE,
)
DOB_PATTERN = re.compile(
    r"\b(?:born|dob|date of birth|birthday)"
    r"\s*[:\-]?\s*\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b",
    re.IGNORECASE,
)
PRIVATE_KEY_PATTERN = re.compile(
    r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----"
)
DB_CONNECTION_PATTERN = re.compile(
    r"(?:postgres|mysql|mongodb|redis)://\S+",
    re.IGNORECASE,
)

# Scope creep: agent trying to do more than asked
_I = re.IGNORECASE

SCOPE_CREEP_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\bi (?:also|additionally)"
        r" (?:found|gathered|collected)\b",
        _I,
    ),
    re.compile(r"\bwhile i was at it\b", _I),
    re.compile(r"\bi went ahead and\b", _I),
    re.compile(r"\bi took the liberty\b", _I),
    re.compile(r"\bbonus:?\s", _I),
]

# Excess data: collecting more than needed
EXCESS_DATA_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bcollect(?:ing|s)?\s+all\b", _I),
    re.compile(
        r"\bstore(?:s|ing)?\s+(?:every|all)\b", _I
    ),
    re.compile(
        r"\bretain(?:s|ing)?\s+indefinitely\b", _I
    ),
    re.compile(
        r"\bno\s+data\s+(?:retention|deletion)\b", _I
    ),
    re.compile(
        r"\bgather(?:s|ing)?\s+(?:as much"
        r"|everything)\b",
        _I,
    ),
]


def check_pii(content: str) -> list[tuple[str, str]]:
    """Check for all PII: shared patterns + address, DOB."""
    hits: list[tuple[str, str]] = []
    for label, pat in PII_PATTERNS:
        for match in pat.finditer(content):
            hits.append((label, match.group()))
    for name, pat in (
        ("address", ADDRESS_PATTERN),
        ("date_of_birth", DOB_PATTERN),
    ):
        for match in pat.finditer(content):
            hits.append((name, match.group()))
    return hits


def check_secrets(content: str) -> list[tuple[str, str]]:
    """Check for all secrets: shared + private keys, DB strings."""
    hits: list[tuple[str, str]] = []
    for label, pat in CREDENTIAL_PATTERNS:
        for match in pat.finditer(content):
            hits.append((label, match.group()))
    for name, pat in (
        ("private_key", PRIVATE_KEY_PATTERN),
        ("db_connection", DB_CONNECTION_PATTERN),
    ):
        for match in pat.finditer(content):
            hits.append((name, match.group()))
    return hits


def check_scope_creep(content: str) -> list[str]:
    """Detect scope creep patterns."""
    matches: list[str] = []
    for pat in SCOPE_CREEP_PATTERNS:
        m = pat.search(content)
        if m:
            matches.append(m.group())
    return matches


def check_excess_data(content: str) -> list[str]:
    """Detect excess data collection patterns."""
    matches: list[str] = []
    for pat in EXCESS_DATA_PATTERNS:
        m = pat.search(content)
        if m:
            matches.append(m.group())
    return matches


class PrivacyLens:
    """Evaluates data minimization, PII, consent, restraint.

    Detection order (strict dominance):
    1. PII detected -> BLOCKED
    2. Secrets detected -> BLOCKED
    3. Scope creep -> ESCALATE
    4. Excess data collection -> ESCALATE
    5. Engine rule evaluation -> per-rule status
    """

    def __init__(
        self,
        engine: GovernanceEngine | None = None,
    ) -> None:
        self._engine = engine

    @property
    def name(self) -> str:
        return "privacy"

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
        - satisfied, no evidence: -0.03
        - satisfied, 1 evidence: -0.02
        - uncertain: -0.12
        """
        conf = DEFAULT_CONFIDENCE
        if uncertain:
            conf -= 0.12
        elif evidence_count == 0:
            conf -= 0.03
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
                    policy_id="privacy-pii",
                    message=(
                        f"PII exposure: {', '.join(h[0] for h in pii_hits)}"
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
                    policy_id="privacy-secrets",
                    message=(
                        f"Secret exposure: "
                        f"{', '.join(h[0] for h in secret_hits)}"
                    ),
                    evidence=[
                        Evidence(
                            claim=f"Secret type '{t}'",
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

        # 3. Scope creep -> ESCALATE
        creep_hits = check_scope_creep(content)
        if creep_hits:
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.ESCALATE,
                    policy_id="privacy-scope-creep",
                    message="Scope creep detected in content",
                    evidence=[
                        Evidence(
                            claim=f"Scope creep: {hit}",
                            source="artifact",
                            pointer="design",
                        )
                        for hit in creep_hits
                    ],
                    confidence=self._calculate_confidence(
                        len(creep_hits),
                        uncertain=True,
                    ),
                )
            )

        # 4. Excess data collection -> ESCALATE
        excess_hits = check_excess_data(content)
        if excess_hits:
            findings.append(
                LensFinding(
                    lens=self.name,
                    status=GovernanceState.ESCALATE,
                    policy_id="privacy-excess-data",
                    message=(
                        "Excess data collection pattern detected"
                    ),
                    evidence=[
                        Evidence(
                            claim=f"Excess data: {hit}",
                            source="artifact",
                            pointer="design",
                        )
                        for hit in excess_hits
                    ],
                    confidence=self._calculate_confidence(
                        len(excess_hits),
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
