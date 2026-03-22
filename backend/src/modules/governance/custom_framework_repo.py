"""Repository for custom governance frameworks."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.governance.custom_framework_models import (
    CustomFrameworkModel,
)
from modules.templates.constants import DEFAULT_SCHEMA_VERSION


class SqlCustomFrameworkRepository:
    """Persists custom frameworks to the database."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        project_id: str,
        framework_id: str,
        name: str,
        version: str = DEFAULT_SCHEMA_VERSION,
        description: str = "",
        categories: list[str] | None = None,
    ) -> CustomFrameworkModel:
        model = CustomFrameworkModel(
            project_id=project_id,
            framework_id=framework_id,
            name=name,
            version=version,
            description=description,
            categories=categories or [],
        )
        self.db.add(model)
        await self.db.flush()
        return model

    async def get_by_id(
        self, framework_id: str
    ) -> CustomFrameworkModel | None:
        result = await self.db.execute(
            select(CustomFrameworkModel).where(
                CustomFrameworkModel.framework_id
                == framework_id
            )
        )
        return result.scalar_one_or_none()

    async def list_by_project(
        self, project_id: str
    ) -> list[CustomFrameworkModel]:
        result = await self.db.execute(
            select(CustomFrameworkModel).where(
                CustomFrameworkModel.project_id == project_id,
                CustomFrameworkModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def delete(self, framework_id: str) -> bool:
        model = await self.get_by_id(framework_id)
        if model is None:
            return False
        await self.db.delete(model)
        await self.db.flush()
        return True
