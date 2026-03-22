"""Business logic for design module."""

from __future__ import annotations

from ideanance.modules.design.models import Design
from ideanance.modules.design.protocols import DesignRepo
from ideanance.modules.design.schemas import DesignCreate


class DesignService:
    def __init__(self, repo: DesignRepo) -> None:
        self.repo = repo

    async def create_design(
        self, project_id: str, data: DesignCreate
    ) -> Design:
        return await self.repo.create(
            project_id=project_id, **data.model_dump()
        )

    async def get_design(self, design_id: str) -> Design | None:
        return await self.repo.get_by_id(design_id)

    async def list_designs(self, project_id: str) -> list[Design]:
        return await self.repo.list_by_project(project_id)

    async def update_design(
        self, design_id: str, **kwargs: object
    ) -> Design | None:
        return await self.repo.update(design_id, **kwargs)
