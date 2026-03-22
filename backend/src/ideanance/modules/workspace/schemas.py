"""Pydantic request/response schemas for workspace module."""

from datetime import datetime

from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""


class WorkspaceRead(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""


class ProjectRead(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
