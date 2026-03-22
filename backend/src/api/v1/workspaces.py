"""Workspace and project endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_workspace_service
from modules.workspace.schemas import (
    ProjectCreate,
    ProjectRead,
    WorkspaceCreate,
    WorkspaceRead,
)
from modules.workspace.service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("/", response_model=WorkspaceRead, status_code=201)
async def create_workspace(
    data: WorkspaceCreate,
    svc: WorkspaceService = Depends(get_workspace_service),
) -> WorkspaceRead:
    workspace = await svc.create_workspace(data)
    return WorkspaceRead.model_validate(workspace)


@router.get("/", response_model=list[WorkspaceRead])
async def list_workspaces(
    svc: WorkspaceService = Depends(get_workspace_service),
) -> list[WorkspaceRead]:
    workspaces = await svc.list_workspaces()
    return [WorkspaceRead.model_validate(w) for w in workspaces]


@router.get("/{workspace_id}", response_model=WorkspaceRead)
async def get_workspace(
    workspace_id: str,
    svc: WorkspaceService = Depends(get_workspace_service),
) -> WorkspaceRead:
    workspace = await svc.get_workspace(workspace_id)
    if workspace is None:
        raise HTTPException(404, "Workspace not found")
    return WorkspaceRead.model_validate(workspace)


@router.post(
    "/{workspace_id}/projects", response_model=ProjectRead, status_code=201
)
async def create_project(
    workspace_id: str,
    data: ProjectCreate,
    svc: WorkspaceService = Depends(get_workspace_service),
) -> ProjectRead:
    try:
        project = await svc.create_project(workspace_id, data)
    except ValueError as e:
        raise HTTPException(404, str(e)) from None
    return ProjectRead.model_validate(project)


@router.get("/{workspace_id}/projects", response_model=list[ProjectRead])
async def list_projects(
    workspace_id: str,
    svc: WorkspaceService = Depends(get_workspace_service),
) -> list[ProjectRead]:
    projects = await svc.list_projects(workspace_id)
    return [ProjectRead.model_validate(p) for p in projects]
