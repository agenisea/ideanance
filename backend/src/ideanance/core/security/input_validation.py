"""Input validation constants and utilities."""

from __future__ import annotations

MAX_DESIGN_CONTENT_SIZE = 100_000  # 100KB per design artifact
MAX_POLICY_YAML_SIZE = 50_000  # 50KB per policy upload
MAX_PROMPT_LENGTH = 10_000  # 10K chars per agent prompt
ALLOWED_UPLOAD_TYPES = frozenset(
    {"text/yaml", "text/markdown", "application/json", "text/plain"}
)


def validate_content_size(
    content: str, max_size: int = MAX_DESIGN_CONTENT_SIZE
) -> bool:
    """Check if content is within size limits."""
    return len(content.encode("utf-8")) <= max_size


def validate_content_type(content_type: str) -> bool:
    """Check if content type is allowed."""
    return content_type in ALLOWED_UPLOAD_TYPES
