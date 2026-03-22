"""Custom governance framework CRUD endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from dependencies import (
    get_custom_framework_service,
)
from modules.governance.custom_framework import (
    CustomFrameworkService,
    YamlValidationError,
)
from modules.templates.constants import DEFAULT_SCHEMA_VERSION

router = APIRouter(prefix="/frameworks", tags=["frameworks"])


# --- Schemas ---


class FrameworkCreateRequest(BaseModel):
    framework_id: str
    name: str
    version: str = DEFAULT_SCHEMA_VERSION
    description: str = ""
    categories: list[str] = []


class FrameworkRead(BaseModel):
    id: str
    project_id: str
    name: str
    version: str
    description: str
    categories: list[str]
    policy_count: int


class PolicyYamlUpload(BaseModel):
    yaml_content: str


class ValidationRead(BaseModel):
    valid: bool
    errors: list[str]
    warnings: list[str]
    policy_count: int
    rule_count: int


# --- Endpoints ---


@router.post("/projects/{project_id}", response_model=FrameworkRead, status_code=201)
async def create_framework(
    project_id: str,
    data: FrameworkCreateRequest,
    svc: CustomFrameworkService = Depends(get_custom_framework_service),
) -> FrameworkRead:
    try:
        fw = svc.create_framework(
            project_id=project_id,
            framework_id=data.framework_id,
            name=data.name,
            version=data.version,
            description=data.description,
            categories=data.categories,
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    return FrameworkRead(
        id=fw.id,
        project_id=fw.project_id,
        name=fw.name,
        version=fw.version,
        description=fw.description,
        categories=fw.categories,
        policy_count=len(fw.policies),
    )


@router.get("/projects/{project_id}", response_model=list[FrameworkRead])
async def list_frameworks(
    project_id: str,
    svc: CustomFrameworkService = Depends(get_custom_framework_service),
) -> list[FrameworkRead]:
    frameworks = svc.list_frameworks(project_id)
    return [
        FrameworkRead(
            id=fw.id,
            project_id=fw.project_id,
            name=fw.name,
            version=fw.version,
            description=fw.description,
            categories=fw.categories,
            policy_count=len(fw.policies),
        )
        for fw in frameworks
    ]


@router.post("/{framework_id}/policies", response_model=dict[str, Any], status_code=201)
async def add_policy(
    framework_id: str,
    body: PolicyYamlUpload,
    svc: CustomFrameworkService = Depends(get_custom_framework_service),
) -> dict[str, Any]:
    try:
        policy = svc.add_policy_from_yaml(framework_id, body.yaml_content)
    except YamlValidationError as e:
        raise HTTPException(422, str(e)) from None
    except ValueError as e:
        raise HTTPException(404, str(e)) from None
    return {
        "id": policy.id,
        "framework": policy.framework,
        "name": policy.name,
        "category": policy.category,
        "severity": policy.severity,
        "rule_count": len(policy.rules),
    }


@router.get("/{framework_id}/validate", response_model=ValidationRead)
async def validate_framework(
    framework_id: str,
    svc: CustomFrameworkService = Depends(get_custom_framework_service),
) -> ValidationRead:
    try:
        result = svc.validate_framework(framework_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from None
    return ValidationRead(
        valid=result.valid,
        errors=result.errors,
        warnings=result.warnings,
        policy_count=result.policy_count,
        rule_count=result.rule_count,
    )


@router.get("/{framework_id}/export")
async def export_framework(
    framework_id: str,
    svc: CustomFrameworkService = Depends(get_custom_framework_service),
) -> dict[str, str]:
    try:
        yaml_content = svc.export_framework_yaml(framework_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from None
    return {"yaml": yaml_content}


@router.delete("/{framework_id}", status_code=204)
async def delete_framework(
    framework_id: str,
    svc: CustomFrameworkService = Depends(get_custom_framework_service),
) -> None:
    try:
        svc.delete_framework(framework_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from None
