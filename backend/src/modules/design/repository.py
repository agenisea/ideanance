"""Data access layer for design module."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import DEFAULT_LIST_LIMIT
from modules.design.models import Design


class SqlDesignRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, project_id: str, **kwargs: object) -> Design:
        design = Design(project_id=project_id, **kwargs)
        self.db.add(design)
        await self.db.flush()
        return design

    async def get_by_id(self, design_id: str) -> Design | None:
        return await self.db.get(Design, design_id)

    async def list_by_project(
        self, project_id: str, limit: int = DEFAULT_LIST_LIMIT
    ) -> list[Design]:
        result = await self.db.execute(
            select(Design)
            .where(Design.project_id == project_id)
            .where(Design.deleted_at.is_(None))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, design_id: str, **kwargs: object) -> Design | None:
        design = await self.db.get(Design, design_id)
        if design is None:
            return None
        for key, value in kwargs.items():
            setattr(design, key, value)
        await self.db.flush()
        return design
