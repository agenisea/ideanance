"""Export endpoints for handoff package generation and download."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from dependencies import get_export_service
from modules.export.schemas import ExportPreview
from modules.export.service import ExportService

router = APIRouter(prefix="/exports", tags=["exports"])


@router.get(
    "/projects/{project_id}/preview",
    response_model=ExportPreview,
)
async def preview_export(
    project_id: str,
    svc: ExportService = Depends(get_export_service),
) -> ExportPreview:
    try:
        return await svc.preview(project_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from None


@router.post("/projects/{project_id}/generate")
async def generate_export(
    project_id: str,
    svc: ExportService = Depends(get_export_service),
) -> dict:
    try:
        package = await svc.generate_package(project_id)
        return {
            "project_name": package.project_name,
            "artifact_count": len(package.artifacts) + 2,
            "ai_context_yml": package.ai_context_yml,
        }
    except ValueError as e:
        raise HTTPException(404, str(e)) from None


@router.get("/projects/{project_id}/download")
async def download_export(
    project_id: str,
    svc: ExportService = Depends(get_export_service),
) -> Response:
    try:
        zip_bytes = await svc.download_zip(project_id)
        fname = f"ideanance-export-{project_id}.zip"
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{fname}"'
            },
        )
    except ValueError as e:
        raise HTTPException(404, str(e)) from None
