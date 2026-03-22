"""Context window assembly for agents.

Infrastructure-level: session in constructor (like Sql* repos).
AsyncSession must NOT appear in method parameters.
"""

from __future__ import annotations

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ideanance.modules.governance.chunk_models import GovernanceChunk
from ideanance.modules.governance.retrieval import RetrievalResult

log = structlog.get_logger()

# Base token budget for single-framework context
CONTEXT_TOKEN_BUDGET_BASE = 4000

# Extra budget per additional framework
CONTEXT_TOKEN_BUDGET_PER_EXTRA_FRAMEWORK = 2000

# Approximate chars per token (conservative estimate for English text)
CONTEXT_CHAR_ESTIMATE_FACTOR = 4


def compute_context_budget(framework_count: int) -> int:
    """Dynamic budget based on active framework count.

    Pure function — belongs in context_assembly, not retrieval.
    1 framework: 4,000 tokens
    2 frameworks: 6,000 tokens
    3 frameworks: 8,000 tokens
    """
    return CONTEXT_TOKEN_BUDGET_BASE + (
        CONTEXT_TOKEN_BUDGET_PER_EXTRA_FRAMEWORK * max(0, framework_count - 1)
    )


class ContextAssembler:
    """Assembles retrieved chunks into a structured context window."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def assemble(
        self,
        results: list[RetrievalResult],
        framework_count: int = 1,
    ) -> str:
        """Assemble results into structured context for LLM."""
        log.info(
            "context_assembly.assembling",
            result_count=len(results),
            framework_count=framework_count,
        )
        enriched = await self._fetch_parents(results)
        deduped = self._deduplicate(enriched)
        budget = compute_context_budget(framework_count)
        truncated = self._truncate_to_budget(deduped, budget)
        return self._format_context(truncated)

    async def _fetch_parents(
        self, results: list[RetrievalResult]
    ) -> list[RetrievalResult]:
        """Enrich with parent sections for hierarchy context."""
        parent_ids = {
            r.section_id for r in results if r.section_id
        }
        # Find chunks that have parent_chunk_id referencing our results
        # and also fetch parents of our results
        section_ids = [r.section_id for r in results]
        if not section_ids:
            return results

        # Query for parent chunks referenced by our result chunks
        stmt = select(GovernanceChunk).where(
            GovernanceChunk.section_id.in_(section_ids)
        )
        db_result = await self.db.execute(stmt)
        db_chunks = {c.section_id: c for c in db_result.scalars().all()}

        enriched = list(results)
        parent_section_ids: set[str] = set()

        for chunk in db_chunks.values():
            if chunk.parent_chunk_id and chunk.parent_chunk_id not in parent_ids:
                parent_section_ids.add(chunk.parent_chunk_id)

        if parent_section_ids:
            parent_stmt = select(GovernanceChunk).where(
                GovernanceChunk.section_id.in_(list(parent_section_ids))
            )
            parent_result = await self.db.execute(parent_stmt)
            for parent in parent_result.scalars().all():
                if parent.section_id not in parent_ids:
                    enriched.append(
                        RetrievalResult(
                            chunk_id=parent.id,
                            content=parent.content,
                            framework=parent.framework,
                            category=parent.category,
                            section_id=parent.section_id,
                            section_title=parent.section_title,
                            score=0.0,
                        )
                    )
                    parent_ids.add(parent.section_id)

        return enriched

    def _deduplicate(
        self, results: list[RetrievalResult]
    ) -> list[RetrievalResult]:
        """Remove near-duplicate chunks by section_id."""
        seen: set[str] = set()
        deduped = []
        for r in results:
            if r.section_id not in seen:
                seen.add(r.section_id)
                deduped.append(r)
        return deduped

    def _truncate_to_budget(
        self,
        results: list[RetrievalResult],
        token_budget: int = CONTEXT_TOKEN_BUDGET_BASE,
    ) -> list[RetrievalResult]:
        """Keep chunks within token budget (rough char estimate)."""
        total_chars = 0
        truncated = []
        char_limit = token_budget * CONTEXT_CHAR_ESTIMATE_FACTOR
        for r in results:
            chunk_chars = len(r.content) + len(r.section_title) + 50
            if total_chars + chunk_chars > char_limit:
                break
            total_chars += chunk_chars
            truncated.append(r)
        return truncated

    def _format_context(
        self, chunks: list[RetrievalResult]
    ) -> str:
        """Format with section markers for LLM citation."""
        if not chunks:
            return ""
        sections = []
        for chunk in chunks:
            sections.append(
                f"[{chunk.framework} — "
                f"{chunk.section_id}: {chunk.section_title}]\n"
                f"{chunk.content}"
            )
        return "\n---\n".join(sections)
