"""Analytics endpoints — governance metrics."""

from typing import Any

from fastapi import APIRouter, Depends

from ideanance.dependencies import get_analytics_service
from ideanance.modules.analytics.service import (
    AnalyticsService,
)

router = APIRouter(
    prefix="/analytics", tags=["analytics"]
)


@router.get("/projects/{project_id}/score")
async def get_project_score(
    project_id: str,
    svc: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> dict[str, Any]:
    score = await svc.get_project_score(project_id)
    return {"project_id": project_id, "score": score}


@router.get("/projects/{project_id}/coverage")
async def get_coverage(
    project_id: str,
    svc: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> dict[str, Any]:
    coverage = await svc.get_coverage(project_id)
    return {
        "project_id": project_id,
        "coverage": coverage,
    }


@router.post("/projects/{project_id}/snapshot")
async def create_snapshot(
    project_id: str,
    svc: AnalyticsService = Depends(
        get_analytics_service
    ),
) -> dict[str, Any]:
    snapshot = await svc.create_snapshot(
        project_id, workspace_id=""
    )
    return {
        "project_id": project_id,
        "score": snapshot.overall_score,
        "policies_active": snapshot.policies_active,
        "frameworks_active": snapshot.frameworks_active,
        "snapshot_date": snapshot.snapshot_date,
    }
