"""Scan user-submitted content for accidentally leaked secrets."""

from __future__ import annotations

import re
from dataclasses import dataclass

SECRET_PATTERNS: list[tuple[str, str]] = [
    (r"sk-ant-[a-zA-Z0-9_-]{20,}", "Anthropic API Key"),
    (r"sk-[a-zA-Z0-9]{20,}", "OpenAI API Key"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token"),
    (r"glpat-[a-zA-Z0-9_-]{20}", "GitLab Personal Access Token"),
    (r"xox[bsp]-[a-zA-Z0-9-]+", "Slack Token"),
    (r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----", "Private Key"),
    (
        r"password\s*[:=]\s*[\"'][^\"']{8,}",
        "Hardcoded Password",
    ),
]

# Compiled for performance
_COMPILED = [(re.compile(p), name) for p, name in SECRET_PATTERNS]


@dataclass
class SecretFinding:
    pattern_name: str
    count: int


def detect_secrets(content: str) -> list[SecretFinding]:
    """Scan content for potential secrets. Returns list of findings.

    Never includes the actual secret value in the finding.
    """
    findings: list[SecretFinding] = []
    for pattern, name in _COMPILED:
        matches = pattern.findall(content)
        if matches:
            findings.append(SecretFinding(pattern_name=name, count=len(matches)))
    return findings


def has_secrets(content: str) -> bool:
    """Quick check: does content contain any detectable secrets?"""
    return len(detect_secrets(content)) > 0
