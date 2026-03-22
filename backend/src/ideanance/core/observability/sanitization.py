"""PII sanitization — strict/moderate/permissive modes."""

from __future__ import annotations

import hashlib
from enum import StrEnum
from typing import Any


class SanitizationMode(StrEnum):
    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"


PII_FIELDS = frozenset(
    {
        "user_message",
        "response",
        "email",
        "name",
        "phone",
        "project_name",
        "agent_spec_content",
        "policy_content",
        "framework_section",
    }
)
HASH_FIELDS = frozenset({"session_id", "user_id"})


def _hash_value(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def sanitize(
    data: dict[str, Any],
    mode: SanitizationMode = SanitizationMode.STRICT,
) -> dict[str, Any]:
    """Sanitize data based on mode."""
    if mode == SanitizationMode.PERMISSIVE:
        return data

    result: dict[str, Any] = {}
    for key, value in data.items():
        if key in PII_FIELDS:
            if mode == SanitizationMode.STRICT:
                result[key] = "[REDACTED]"
            else:
                result[key] = _hash_value(str(value))
        elif key in HASH_FIELDS:
            result[key] = _hash_value(str(value))
        elif isinstance(value, dict):
            result[key] = sanitize(value, mode)
        else:
            result[key] = value
    return result
