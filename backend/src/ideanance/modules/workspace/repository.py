"""Data access layer for workspace module."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ideanance.core.constants import DEFAULT_LIST_LIMIT
from ideanance.modules.workspace.models import Project, Workspace


class SqlWorkspaceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **kwargs: object) -> Workspace:
        workspace = Workspace(**kwargs)
        self.db.add(workspace)
        await self.db.flush()
        return workspace

    async def get_by_id(self, workspace_id: str) -> Workspace | None:
        return await self.db.get(Workspace, workspace_id)

    async def list_all(
        self, limit: int = DEFAULT_LIST_LIMIT, offset: int = 0
    ) -> list[Workspace]:
        result = await self.db.execute(
            select(Workspace).limit(limit).offset(offset)
        )
        return list(result.scalars().all())


class SqlProjectRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, workspace_id: str, **kwargs: object) -> Project:
        project = Project(workspace_id=workspace_id, **kwargs)
        self.db.add(project)
        await self.db.flush()
        return project

    async def get_by_id(self, project_id: str) -> Project | None:
        return await self.db.get(Project, project_id)

    async def list_by_workspace(
        self, workspace_id: str, limit: int = DEFAULT_LIST_LIMIT
    ) -> list[Project]:
        result = await self.db.execute(
            select(Project)
            .where(Project.workspace_id == workspace_id)
            .where(Project.deleted_at.is_(None))
            .limit(limit)
        )
        return list(result.scalars().all())
