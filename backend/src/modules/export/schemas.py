"""Pydantic schemas for the handoff export package."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from modules.export.constants import (
    EXPORT_FORMAT_CLAUDE_CODE,
    EXPORT_VERSION,
    IDEANANCE_VERSION,
)


class ExportArtifact(BaseModel):
    """A single file in the handoff package."""

    filename: str
    content: str
    checksum: str = ""
    governance_provenance: list[str] = Field(default_factory=list)


class HandoffPackage(BaseModel):
    """The complete handoff package structure."""

    project_name: str
    project_id: str
    ai_context_yml: str
    provenance_json: str
    artifacts: list[ExportArtifact] = Field(default_factory=list)
    exported_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


class ExportPreview(BaseModel):
    """Preview of the handoff package (no download)."""

    project_name: str
    governance_score: float
    active_policy_count: int
    wiring_count: int
    artifact_filenames: list[str]
    ai_context_yml: str


class ProvenanceMetadata(BaseModel):
    """Export provenance for audit trail."""

    export_version: str = EXPORT_VERSION
    ideanance_version: str = IDEANANCE_VERSION
    exported_at: str
    project_id: str
    project_name: str
    governance_frameworks: list[str]
    governance_score_at_export: float
    artifact_count: int
    export_config: dict = Field(
        default_factory=lambda: {
            "format": EXPORT_FORMAT_CLAUDE_CODE,
            "include_prompts": True,
            "include_test_cases": True,
        }
    )
