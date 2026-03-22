"""Shared regex patterns for governance lenses.

Contains PII detection and credential detection patterns used by the Boundary
and Privacy lenses.

Design rationale:
- DRY: single source of truth for detection patterns
- OCP: add new patterns here without modifying lens logic
- SRP: pattern definition is separate from pattern usage
"""

from __future__ import annotations

import re

# =========================================================================
# PII DETECTION PATTERNS
# =========================================================================

#: Email address pattern (RFC 5322 simplified)
EMAIL_PATTERN: re.Pattern[str] = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

#: US phone number pattern (with optional country code)
PHONE_PATTERN: re.Pattern[str] = re.compile(
    r"(?:\+?1[-.\s]?)?(?:\([0-9]{3}\)|[0-9]{3})[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}"
)

#: Social Security Number pattern (XXX-XX-XXXX or XXXXXXXXX)
SSN_PATTERN: re.Pattern[str] = re.compile(
    r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"
)

#: Credit card number pattern (16 digits with optional separators)
CREDIT_CARD_PATTERN: re.Pattern[str] = re.compile(
    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
)

# =========================================================================
# CREDENTIAL DETECTION PATTERNS
# =========================================================================

#: API key / secret / token pattern.
#: Matches: api_key=xxx, secret: xxx, token=xxx, etc. (16+ char values)
API_KEY_PATTERN: re.Pattern[str] = re.compile(
    r"(?i)"
    r"(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token"
    r"|bearer|password|secret|token)"
    r"""[\s:=]+['"]?[a-zA-Z0-9_-]{16,}['"]?"""
)

#: AWS access key pattern (all AWS key prefixes).
#: Includes: AKIA (user), ABIA (STS), ACCA (catalog), AGPA (group),
#: AIDA (IAM user), AIPA (EC2), ANPA (managed policy), ANVA (version),
#: AROA (role), ASCA (cert), ASIA (temp STS)
AWS_KEY_PATTERN: re.Pattern[str] = re.compile(
    r"(?i)(AKIA|ABIA|ACCA|AGPA|AIDA|AIPA|ANPA|ANVA|AROA|ASCA|ASIA)[A-Z0-9]{16}"
)

# =========================================================================
# PATTERN COLLECTIONS (for iteration)
# =========================================================================

PII_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("email", EMAIL_PATTERN),
    ("phone", PHONE_PATTERN),
    ("ssn", SSN_PATTERN),
    ("credit_card", CREDIT_CARD_PATTERN),
]

CREDENTIAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("api_key", API_KEY_PATTERN),
    ("aws_key", AWS_KEY_PATTERN),
]


# =========================================================================
# UTILITY FUNCTIONS
# =========================================================================


def find_pattern_matches(
    content: str,
    pattern: re.Pattern[str],
    label: str,
) -> list[tuple[str, int, int]]:
    """Find all matches of *pattern* in *content*.

    Returns:
        A list of ``(label, start, end)`` tuples where *start* and *end*
        are character offsets into *content*.
    """
    return [(label, m.start(), m.end()) for m in pattern.finditer(content)]


def contains_pii(content: str) -> bool:
    """Return ``True`` if *content* contains any PII pattern.

    Checks email, phone, SSN, and credit card patterns.
    """
    return any(pat.search(content) for _, pat in PII_PATTERNS)


def contains_credentials(content: str) -> bool:
    """Return ``True`` if *content* contains any credential pattern.

    Checks API key/secret/token patterns and AWS access key prefixes.
    """
    return any(pat.search(content) for _, pat in CREDENTIAL_PATTERNS)
