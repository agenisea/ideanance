"""HTML sanitization for user-submitted content."""

from __future__ import annotations

import re

# Safe HTML tags (subset for governance content)
SAFE_TAGS = {"p", "br", "strong", "em", "code", "pre", "ul", "ol", "li", "a"}

# Pattern to match HTML tags
_TAG_PATTERN = re.compile(r"<(/?)(\w+)([^>]*)>", re.DOTALL)

# Pattern to strip event handlers and javascript: URLs
_DANGEROUS_ATTRS = re.compile(
    r'\s*(?:on\w+|style)\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]*)',
    re.IGNORECASE,
)
_JS_URL = re.compile(r"javascript:", re.IGNORECASE)


def sanitize_html(content: str) -> str:
    """Sanitize HTML content, keeping only safe tags.

    Strips script tags, event handlers, and dangerous attributes.
    For production, consider using nh3 (Rust-based) for better performance.
    """
    # Remove script and style blocks entirely
    content = re.sub(
        r"<(script|style)[^>]*>.*?</\1>", "", content, flags=re.DOTALL | re.IGNORECASE
    )

    def replace_tag(match: re.Match) -> str:
        slash = match.group(1)
        tag = match.group(2).lower()
        attrs = match.group(3)

        if tag not in SAFE_TAGS:
            return ""

        # Strip dangerous attributes
        attrs = _DANGEROUS_ATTRS.sub("", attrs)
        attrs = _JS_URL.sub("", attrs)

        if attrs.strip():
            return f"<{slash}{tag}{attrs}>"
        return f"<{slash}{tag}>"

    return _TAG_PATTERN.sub(replace_tag, content)


def fence_user_content(content: str) -> str:
    """Wrap user content in XML delimiters to prevent prompt injection."""
    return f"<user_content>\n{content}\n</user_content>"
