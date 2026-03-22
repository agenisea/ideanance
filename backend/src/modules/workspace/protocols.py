"""Protocol interfaces for workspace repositories."""

from __future__ import annotations

from typing import Protocol

from core.constants import DEFAULT_LIST_LIMIT
from modules.workspace.models import Project, Workspace


class WorkspaceRepository(Protocol):
    async def create(self, **kwargs: object) -> Workspace: ...
    async def get_by_id(self, workspace_id: str) -> Workspace | None: ...
    async def list_all(
        self, limit: int = DEFAULT_LIST_LIMIT, offset: int = 0
    ) -> list[Workspace]: ...


class ProjectRepository(Protocol):
    async def create(
        self, workspace_id: str, **kwargs: object
    ) -> Project: ...
    async def get_by_id(self, project_id: str) -> Project | None: ...
    async def list_by_workspace(
        self, workspace_id: str, limit: int = DEFAULT_LIST_LIMIT
    ) -> list[Project]: ...
