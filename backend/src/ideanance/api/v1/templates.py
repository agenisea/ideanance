"""Template export/import endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import Response

from ideanance.dependencies import get_template_service
from ideanance.modules.templates.packager import (
    TemplatePackageError,
)
from ideanance.modules.templates.schemas import (
    BuiltinExportRequest,
    BuiltinFrameworkInfo,
    TemplateImportResponse,
)
from ideanance.modules.templates.service import TemplateService

router = APIRouter(
    prefix="/templates", tags=["templates"]
)


@router.post("/export")
async def export_builtin(
    body: BuiltinExportRequest,
    svc: TemplateService = Depends(get_template_service),
) -> Response:
    """Export a built-in framework as a downloadable ZIP."""
    try:
        zip_bytes = svc.export_builtin(body.framework_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from None

    filename = f"{body.framework_id}-template.zip"
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )


@router.post(
    "/import", response_model=TemplateImportResponse
)
async def import_template(
    file: UploadFile,
    svc: TemplateService = Depends(get_template_service),
) -> TemplateImportResponse:
    """Import a governance framework from a ZIP file."""
    zip_bytes = await file.read()

    try:
        manifest, policies = svc.import_framework(zip_bytes)
    except TemplatePackageError as e:
        raise HTTPException(422, str(e)) from None

    return TemplateImportResponse(
        framework_name=manifest.get("name", ""),
        version=manifest.get("version", "1.0.0"),
        author=manifest.get("author", ""),
        description=manifest.get("description", ""),
        policy_count=len(policies),
        policy_ids=[p.id for p in policies],
    )


@router.get(
    "/builtin",
    response_model=list[BuiltinFrameworkInfo],
)
async def list_builtin_frameworks(
    svc: TemplateService = Depends(get_template_service),
) -> list[BuiltinFrameworkInfo]:
    """List built-in frameworks available for export."""
    frameworks = svc.list_builtin_frameworks()
    return [
        BuiltinFrameworkInfo(
            id=fw["id"], name=fw["name"]
        )
        for fw in frameworks
    ]
