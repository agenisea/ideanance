"""Rule-level structural chunking for governance policies.

Each rule becomes its own chunk with parent_chunk_id pointing
to the policy chunk. Improves retrieval precision.
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.governance.loader import LoadedPolicy


@dataclass
class Chunk:
    """A chunk ready for embedding and storage."""

    content: str
    framework: str
    category: str
    section_id: str
    section_title: str
    chunk_type: str
    parent_chunk_id: str | None = None
    token_count: int = 0


class GovernanceChunker:
    """Chunks governance policies at the rule level."""

    def chunk_policy(self, policy: LoadedPolicy) -> list[Chunk]:
        """Chunk a policy into parent + rule + remediation chunks."""
        chunks = []

        # Policy-level parent chunk (description only)
        parent_text = f"{policy.name}\n{policy.description}"
        chunks.append(
            Chunk(
                content=parent_text.strip(),
                framework=policy.framework,
                category=policy.category,
                section_id=policy.id,
                section_title=policy.name,
                chunk_type="subcategory",
                token_count=len(parent_text.split()),
            )
        )

        # Rule-level child chunks
        for i, rule in enumerate(policy.rules):
            rule_text = (
                f"{rule.message}"
                f" (check: {rule.check},"
                f" target: {rule.target})"
            )
            chunks.append(
                Chunk(
                    content=rule_text,
                    framework=policy.framework,
                    category=policy.category,
                    section_id=f"{policy.id}-rule-{i}",
                    section_title=(
                        f"{policy.name} — Rule {i + 1}"
                    ),
                    chunk_type="rule",
                    parent_chunk_id=policy.id,
                    token_count=len(rule_text.split()),
                )
            )

        # Remediation as child chunk
        guidance = policy.remediation.get("guidance", "")
        if guidance:
            chunks.append(
                Chunk(
                    content=f"Remediation: {guidance}",
                    framework=policy.framework,
                    category=policy.category,
                    section_id=(
                        f"{policy.id}-remediation"
                    ),
                    section_title=(
                        f"{policy.name} — Remediation"
                    ),
                    chunk_type="remediation",
                    parent_chunk_id=policy.id,
                    token_count=len(guidance.split()),
                )
            )

        return chunks
