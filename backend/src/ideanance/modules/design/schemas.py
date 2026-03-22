"""Pydantic request/response schemas for design module."""

from datetime import datetime

from pydantic import BaseModel, Field


class DesignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    design_type: str = Field(pattern="^(agent|pipeline)$")
    content: dict = Field(default_factory=dict)


class DesignRead(BaseModel):
    id: str
    project_id: str
    name: str
    design_type: str
    content: dict
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
