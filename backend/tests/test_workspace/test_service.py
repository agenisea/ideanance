"""Unit tests for WorkspaceService using fake repositories."""

from __future__ import annotations

import pytest

from modules.workspace.schemas import ProjectCreate, WorkspaceCreate
from modules.workspace.service import WorkspaceService
from tests.fakes import FakeProjectRepository, FakeWorkspaceRepository


def _build_service() -> WorkspaceService:
    return WorkspaceService(
        workspace_repo=FakeWorkspaceRepository(),
        project_repo=FakeProjectRepository(),
    )


async def test_create_workspace():
    svc = _build_service()
    ws = await svc.create_workspace(WorkspaceCreate(name="My Workspace"))
    assert ws.name == "My Workspace"
    assert ws.id is not None

    # Should be retrievable
    fetched = await svc.get_workspace(ws.id)
    assert fetched is not None
    assert fetched.name == "My Workspace"


async def test_create_project():
    svc = _build_service()
    ws = await svc.create_workspace(WorkspaceCreate(name="WS"))
    proj = await svc.create_project(
        ws.id, ProjectCreate(name="Project Alpha")
    )
    assert proj.name == "Project Alpha"
    assert proj.workspace_id == ws.id

    # Should appear in list
    projects = await svc.list_projects(ws.id)
    assert len(projects) == 1
    assert projects[0].id == proj.id


async def test_create_project_invalid_workspace_raises():
    svc = _build_service()
    with pytest.raises(ValueError, match="not found"):
        await svc.create_project(
            "nonexistent-ws", ProjectCreate(name="Fail")
        )
