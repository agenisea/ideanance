"""Business logic for workspace module."""

from __future__ import annotations

from ideanance.modules.workspace.models import Project, Workspace
from ideanance.modules.workspace.protocols import (
    ProjectRepository,
    WorkspaceRepository,
)
from ideanance.modules.workspace.schemas import ProjectCreate, WorkspaceCreate


class WorkspaceService:
    def __init__(
        self,
        workspace_repo: WorkspaceRepository,
        project_repo: ProjectRepository,
    ) -> None:
        self.workspace_repo = workspace_repo
        self.project_repo = project_repo

    async def create_workspace(self, data: WorkspaceCreate) -> Workspace:
        return await self.workspace_repo.create(**data.model_dump())

    async def get_workspace(self, workspace_id: str) -> Workspace | None:
        return await self.workspace_repo.get_by_id(workspace_id)

    async def list_workspaces(self) -> list[Workspace]:
        return await self.workspace_repo.list_all()

    async def create_project(
        self, workspace_id: str, data: ProjectCreate
    ) -> Project:
        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if workspace is None:
            raise ValueError(f"Workspace {workspace_id} not found")
        return await self.project_repo.create(
            workspace_id=workspace_id, **data.model_dump()
        )

    async def list_projects(self, workspace_id: str) -> list[Project]:
        return await self.project_repo.list_by_workspace(workspace_id)
