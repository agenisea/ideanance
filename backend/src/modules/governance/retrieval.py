"""Hybrid search: keyword + semantic (pgvector) + RRF.

Infrastructure-level component. Session in constructor.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import structlog
from sqlalchemy import or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import DEFAULT_RETRIEVAL_TOP_K
from core.embeddings import EmbeddingClient
from modules.governance.chunk_models import (
    GovernanceChunk,
)

log = structlog.get_logger()

# RRF smoothing constant (Cormack et al.)
RRF_K = 60

# Keyword search fetches this multiple of top_k for diversity
KEYWORD_EXPANSION_FACTOR = 2


@dataclass
class RetrievalResult:
    """A single search result from the retrieval pipeline."""

    chunk_id: str
    content: str
    framework: str
    category: str
    section_id: str
    section_title: str
    score: float = 0.0


class HybridRetriever:
    """Hybrid search with SQLite keyword fallback.

    On SQLite: keyword-only (LIKE).
    On PostgreSQL: pgvector semantic + keyword + RRF fusion.
    """

    def __init__(
        self,
        db: AsyncSession,
        embedding_client: EmbeddingClient | None = None,
        is_sqlite: bool = True,
    ) -> None:
        self.db = db
        self.embedding_client = embedding_client
        self.is_sqlite = is_sqlite

    async def search(
        self,
        query: str,
        frameworks: list[str],
        top_k: int = DEFAULT_RETRIEVAL_TOP_K,
    ) -> list[RetrievalResult]:
        """Search governance chunks."""
        keyword_results = await self._keyword_search(
            query,
            frameworks,
            top_k=top_k * KEYWORD_EXPANSION_FACTOR,
        )

        if self.is_sqlite or self.embedding_client is None:
            return keyword_results[:top_k]

        # PostgreSQL: semantic + keyword + RRF
        semantic_results = await self._semantic_search(
            query,
            frameworks,
            top_k=top_k * KEYWORD_EXPANSION_FACTOR,
        )
        fused = self._reciprocal_rank_fusion(
            keyword_results, semantic_results
        )
        return fused[:top_k]

    async def _keyword_search(
        self,
        query: str,
        frameworks: list[str],
        top_k: int,
    ) -> list[RetrievalResult]:
        """LIKE-based keyword search (SQLite + PostgreSQL)."""
        terms = query.lower().split()
        if not terms:
            return []

        conditions = [
            GovernanceChunk.content.ilike(f"%{term}%")
            for term in terms[:5]
        ]
        stmt = (
            select(GovernanceChunk)
            .where(
                GovernanceChunk.framework.in_(frameworks),
                or_(*conditions),
            )
            .limit(top_k)
        )
        result = await self.db.execute(stmt)
        chunks = list(result.scalars().all())
        return [self._to_result(c) for c in chunks]

    async def _semantic_search(
        self,
        query: str,
        frameworks: list[str],
        top_k: int,
    ) -> list[RetrievalResult]:
        """pgvector semantic search (PostgreSQL only).

        Uses embedding_json::vector cast for cosine distance.
        """
        if (
            self.is_sqlite
            or self.embedding_client is None
        ):
            return []

        query_embedding = await self.embedding_client.embed(
            query
        )
        query_json = json.dumps(query_embedding)

        # pgvector cosine distance via JSON text cast
        fw_list = ",".join(
            f"'{fw}'" for fw in frameworks
        )
        raw_sql = text(f"""
            SELECT id, content, framework, category,
                   section_id, section_title,
                   (embedding_json::vector <=> :q::vector)
                   AS distance
            FROM governance_chunks
            WHERE framework IN ({fw_list})
            AND embedding_json IS NOT NULL
            ORDER BY distance
            LIMIT :top_k
        """)

        try:
            result = await self.db.execute(
                raw_sql,
                {"q": query_json, "top_k": top_k},
            )
            rows = result.fetchall()
            return [
                RetrievalResult(
                    chunk_id=str(row.id),
                    content=row.content,
                    framework=row.framework,
                    category=row.category,
                    section_id=row.section_id,
                    section_title=row.section_title,
                    score=1.0 - (row.distance or 0),
                )
                for row in rows
            ]
        except Exception:
            log.warning(
                "retrieval.semantic_search_failed",
                msg="pgvector query failed, falling back",
            )
            return []

    @staticmethod
    def _reciprocal_rank_fusion(
        *result_lists: list[RetrievalResult],
        k: int = RRF_K,
    ) -> list[RetrievalResult]:
        """RRF with score threshold filtering."""
        scores: dict[str, float] = {}
        items: dict[str, RetrievalResult] = {}
        for results in result_lists:
            for rank, result in enumerate(results):
                key = result.chunk_id
                scores[key] = (
                    scores.get(key, 0)
                    + 1 / (k + rank + 1)
                )
                items[key] = result

        if not scores:
            return []

        sorted_ids = sorted(
            scores,
            key=lambda x: scores[x],
            reverse=True,
        )

        # RRF threshold: discard below median score
        score_values = sorted(
            scores.values(), reverse=True
        )
        median = score_values[len(score_values) // 2]
        filtered = [
            items[cid]
            for cid in sorted_ids
            if scores[cid] >= median
        ]

        # Update scores on results
        for r in filtered:
            r.score = scores[r.chunk_id]

        return filtered

    def _to_result(
        self, chunk: GovernanceChunk
    ) -> RetrievalResult:
        return RetrievalResult(
            chunk_id=chunk.id,
            content=chunk.content,
            framework=chunk.framework,
            category=chunk.category,
            section_id=chunk.section_id,
            section_title=chunk.section_title,
        )
