"""Pydantic request/response schemas for evaluation module."""

from datetime import datetime

from pydantic import BaseModel, Field


class EvaluationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    design_id: str | None = None


class EvaluationRead(BaseModel):
    id: str
    project_id: str
    design_id: str | None
    name: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EvalCriterionCreate(BaseModel):
    criterion_id: str = Field(min_length=1, max_length=100)
    description: str
    metric: str
    threshold: str
    priority: str = "medium"
    test_cases: dict = Field(default_factory=dict)


class EvalCriterionRead(BaseModel):
    id: str
    evaluation_id: str
    criterion_id: str
    description: str
    metric: str
    threshold: str
    priority: str
    test_cases: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
