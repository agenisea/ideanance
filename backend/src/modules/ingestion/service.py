"""Ingestion service — orchestrates parsing, chunking, embedding, storage.

Constructor-injected per PLAN7_REFACTOR patterns.
"""

from __future__ import annotations

import json
from pathlib import Path

import structlog

from core.embeddings import EmbeddingClient
from core.events import Event, EventBus
from core.observability.context import get_context
from modules.governance.loader import (
    load_framework_policies,
)
from modules.ingestion.chunker import GovernanceChunker
from modules.ingestion.protocols import (
    GovernanceChunkRepo,
)

log = structlog.get_logger()

# Max chunks per embed_batch() call
EMBED_BATCH_SIZE = 100


class IngestionService:
    """Orchestrates governance framework ingestion."""

    def __init__(
        self,
        chunk_repo: GovernanceChunkRepo,
        embedding_client: EmbeddingClient,
        chunker: GovernanceChunker,
        event_bus: EventBus | None = None,
    ) -> None:
        self.chunk_repo = chunk_repo
        self.embedding_client = embedding_client
        self.chunker = chunker
        self.event_bus = event_bus

    async def seed_framework(
        self, framework_dir: Path
    ) -> int:
        """Seed a governance framework from YAML fixtures.

        Embeds chunks in batches during ingestion.
        Returns count of chunks created.
        """
        policies = load_framework_policies(framework_dir)
        all_chunks = []
        for policy in policies:
            all_chunks.extend(
                self.chunker.chunk_policy(policy)
            )

        chunk_count = 0
        for batch_start in range(
            0, len(all_chunks), EMBED_BATCH_SIZE
        ):
            batch = all_chunks[
                batch_start : batch_start + EMBED_BATCH_SIZE
            ]
            texts = [c.content for c in batch]

            # Embed batch
            embeddings = (
                await self.embedding_client.embed_batch(texts)
            )

            for chunk, emb_vector in zip(
                batch, embeddings, strict=True
            ):
                await self.chunk_repo.create(
                    content=chunk.content,
                    framework=chunk.framework,
                    category=chunk.category,
                    section_id=chunk.section_id,
                    section_title=chunk.section_title,
                    chunk_type=chunk.chunk_type,
                    parent_chunk_id=chunk.parent_chunk_id,
                    token_count=chunk.token_count,
                    embedding_json=json.dumps(emb_vector),
                )
                chunk_count += 1

        log.info(
            "ingestion.framework_seeded",
            framework_dir=str(framework_dir),
            chunk_count=chunk_count,
        )

        if self.event_bus:
            ctx = get_context()
            await self.event_bus.publish(
                Event(
                    type="ingestion.framework.seeded",
                    workspace_id=(
                        ctx.workspace_id if ctx else ""
                    ),
                    payload={
                        "framework_dir": str(framework_dir),
                        "chunk_count": chunk_count,
                    },
                )
            )

        return chunk_count

    async def re_embed_framework(
        self, framework_name: str, framework_dir: Path
    ) -> int:
        """Delete existing chunks and re-seed.

        For embedding model changes.
        """
        deleted = (
            await self.chunk_repo.delete_by_framework(
                framework_name
            )
        )
        log.info(
            "ingestion.re_embed",
            framework=framework_name,
            deleted=deleted,
        )
        return await self.seed_framework(framework_dir)
