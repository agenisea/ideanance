"""Tests for PII sanitization."""

from core.observability.sanitization import (
    SanitizationMode,
    sanitize,
)


def test_strict_redacts_pii():
    data = {
        "user_message": "Hello",
        "email": "user@example.com",
        "model": "sonnet",
    }
    result = sanitize(data, SanitizationMode.STRICT)
    assert result["user_message"] == "[REDACTED]"
    assert result["email"] == "[REDACTED]"
    assert result["model"] == "sonnet"  # Preserved


def test_moderate_hashes_pii():
    data = {"user_message": "Hello", "model": "sonnet"}
    result = sanitize(data, SanitizationMode.MODERATE)
    assert result["user_message"] != "Hello"
    assert result["user_message"] != "[REDACTED]"
    assert len(result["user_message"]) == 16  # SHA-256 truncated


def test_permissive_preserves_all():
    data = {"user_message": "Hello", "email": "user@example.com"}
    result = sanitize(data, SanitizationMode.PERMISSIVE)
    assert result == data


def test_hash_fields_always_hashed():
    data = {"session_id": "abc123", "user_id": "user-1"}
    result = sanitize(data, SanitizationMode.STRICT)
    assert result["session_id"] != "abc123"
    assert len(result["session_id"]) == 16


def test_nested_dict_sanitized():
    data = {"meta": {"user_message": "secret", "count": 5}}
    result = sanitize(data, SanitizationMode.STRICT)
    assert result["meta"]["user_message"] == "[REDACTED]"
    assert result["meta"]["count"] == 5
