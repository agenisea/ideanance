"""Pydantic schemas for template export/import API."""

from __future__ import annotations

from pydantic import BaseModel, Field

from modules.templates.constants import DEFAULT_SCHEMA_VERSION


class TemplateExportRequest(BaseModel):
    """Request to export a custom framework as a ZIP."""

    framework_name: str = Field(
        ..., description="Display name of the framework"
    )
    policy_ids: list[str] = Field(
        default_factory=list,
        description="Policy IDs to include (empty = all)",
    )
    version: str = DEFAULT_SCHEMA_VERSION
    description: str = ""
    author: str = ""
    tags: list[str] = Field(default_factory=list)


class BuiltinExportRequest(BaseModel):
    """Request to export a built-in framework."""

    framework_id: str = Field(
        ...,
        description=(
            "Built-in framework ID (nist-ai-rmf, eu-ai-act)"
        ),
    )


class TemplateImportResponse(BaseModel):
    """Response after importing a template ZIP."""

    framework_name: str
    version: str
    author: str
    description: str
    policy_count: int
    policy_ids: list[str]


class BuiltinFrameworkInfo(BaseModel):
    """Info about an available built-in framework."""

    id: str
    name: str
