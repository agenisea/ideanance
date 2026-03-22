"""Tests for input validation utilities."""

from ideanance.core.security.input_validation import (
    ALLOWED_UPLOAD_TYPES,
    MAX_DESIGN_CONTENT_SIZE,
    validate_content_size,
    validate_content_type,
)


def test_accepts_small_content():
    assert validate_content_size("small text") is True


def test_rejects_oversized_content():
    large = "x" * (MAX_DESIGN_CONTENT_SIZE + 1)
    assert validate_content_size(large) is False


def test_exact_limit_accepted():
    content = "x" * MAX_DESIGN_CONTENT_SIZE
    assert validate_content_size(content, MAX_DESIGN_CONTENT_SIZE) is True


def test_custom_limit():
    assert validate_content_size("hello", max_size=5) is True
    assert validate_content_size("hello!", max_size=5) is False


def test_accepts_yaml_content_type():
    assert validate_content_type("text/yaml") is True


def test_accepts_markdown_content_type():
    assert validate_content_type("text/markdown") is True


def test_accepts_json_content_type():
    assert validate_content_type("application/json") is True


def test_rejects_html_content_type():
    assert validate_content_type("text/html") is False


def test_rejects_binary_content_type():
    assert validate_content_type("application/octet-stream") is False


def test_allowed_types_is_frozenset():
    assert isinstance(ALLOWED_UPLOAD_TYPES, frozenset)
