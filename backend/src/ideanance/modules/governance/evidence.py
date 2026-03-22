"""Evidence model — traces findings to their source.

Traces findings to their source with pointers.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    """Traces a finding to its source with a pointer."""

    claim: str
    source: str  # "artifact" | "policy" | "context"
    pointer: str  # "design.purpose" or "nist-govern-1.1"
    excerpt: str = ""
