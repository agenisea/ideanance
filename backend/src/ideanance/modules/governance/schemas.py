"""Pydantic request/response schemas for governance module."""

from datetime import datetime

from pydantic import BaseModel, Field


class GovernancePolicyCreate(BaseModel):
    framework: str
    policy_id: str
    name: str
    description: str = ""
    category: str
    subcategory: str = ""
    severity: str = "warning"
    rules: dict = Field(default_factory=dict)


class GovernancePolicyRead(BaseModel):
    id: str
    project_id: str
    framework: str
    policy_id: str
    name: str
    description: str
    category: str
    subcategory: str
    severity: str
    rules: dict
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GovernanceEvalWiringCreate(BaseModel):
    policy_id: str
    criterion_id: str
    wiring_type: str = "manual"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    rationale: str = ""


class GovernanceEvalWiringRead(BaseModel):
    id: str
    project_id: str
    policy_id: str
    criterion_id: str
    wiring_type: str
    confidence: float
    rationale: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GovernanceCheckRequest(BaseModel):
    project_id: str
    design_content: dict


class GovernanceCheckResponse(BaseModel):
    results: list[dict]
    overall_score: float
