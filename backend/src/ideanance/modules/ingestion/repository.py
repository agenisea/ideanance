"""Data access layer for ingestion module."""

from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ideanance.modules.governance.chunk_models import GovernanceChunk


class SqlGovernanceChunkRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **kwargs: object) -> GovernanceChunk:
        chunk = GovernanceChunk(**kwargs)
        self.db.add(chunk)
        await self.db.flush()
        return chunk

    async def count_by_framework(self, framework: str) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(GovernanceChunk)
            .where(GovernanceChunk.framework == framework)
        )
        return result.scalar_one()

    async def list_by_framework(
        self, framework: str
    ) -> list[GovernanceChunk]:
        result = await self.db.execute(
            select(GovernanceChunk).where(
                GovernanceChunk.framework == framework
            )
        )
        return list(result.scalars().all())

    async def delete_by_framework(
        self, framework: str
    ) -> int:
        result = await self.db.execute(
            delete(GovernanceChunk).where(
                GovernanceChunk.framework == framework
            )
        )
        await self.db.flush()
        return result.rowcount  # type: ignore[return-value]
