"""PII detection with governance content allowlist.

Deterministic regex patterns for governance content.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PII_PATTERNS: list[tuple[re.Pattern, str]] = [
    (
        re.compile(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+"
            r"\.[a-zA-Z]{2,}"
        ),
        "Email Address",
    ),
    (
        re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
        "Phone Number",
    ),
    (
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "SSN",
    ),
    (
        re.compile(
            r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"
        ),
        "Credit Card",
    ),
    (
        re.compile(r"\b[A-Z]{2}\d{6,10}\b"),
        "Government ID",
    ),
]

# Governance content allowlist — suppress false positives
ALLOWLIST_PATTERNS: list[re.Pattern] = [
    re.compile(r"nist-\w+"),
    re.compile(r"eu-art\d+"),
    re.compile(r"EU\d{4}[/]?\d*"),
    re.compile(r"Art\.\s*\d+"),
    re.compile(r"GOVERN-\d+"),
    re.compile(r"MAP-\d+"),
    re.compile(r"MEASURE-\d+"),
    re.compile(r"MANAGE-\d+"),
]


@dataclass(frozen=True)
class PIIFinding:
    pii_type: str
    start: int
    end: int


class PIIDetector:
    """Deterministic PII detection with allowlist."""

    def detect(self, content: str) -> list[PIIFinding]:
        findings: list[PIIFinding] = []
        for pattern, pii_type in PII_PATTERNS:
            for match in pattern.finditer(content):
                if self._is_allowlisted(
                    content, match
                ):
                    continue
                findings.append(
                    PIIFinding(
                        pii_type=pii_type,
                        start=match.start(),
                        end=match.end(),
                    )
                )
        return findings

    def _is_allowlisted(
        self, content: str, match: re.Match
    ) -> bool:
        region = content[
            max(0, match.start() - 20) : match.end() + 20
        ]
        return any(
            p.search(region) for p in ALLOWLIST_PATTERNS
        )

    def has_pii(self, content: str) -> bool:
        return len(self.detect(content)) > 0
