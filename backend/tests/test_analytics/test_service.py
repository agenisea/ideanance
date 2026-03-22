"""Tests for analytics service — PLAN48."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ideanance.modules.analytics.service import (
    AnalyticsService,
)


async def test_project_score_no_snapshot(
    db: AsyncSession,
):
    svc = AnalyticsService(db)
    score = await svc.get_project_score("nonexistent")
    assert score == 0.0


async def test_create_snapshot(db: AsyncSession):
    svc = AnalyticsService(db)
    snapshot = await svc.create_snapshot(
        "proj-1", "ws-1"
    )
    assert snapshot.project_id == "proj-1"
    assert snapshot.snapshot_date is not None


async def test_project_score_after_snapshot(
    db: AsyncSession,
):
    svc = AnalyticsService(db)
    await svc.create_snapshot("proj-2", "ws-1")
    score = await svc.get_project_score("proj-2")
    assert score >= 0.0


async def test_coverage_empty(db: AsyncSession):
    svc = AnalyticsService(db)
    coverage = await svc.get_coverage("nonexistent")
    assert coverage == {}


async def test_analytics_api_snapshot(
    client: AsyncClient,
):
    # Create workspace + project first
    resp = await client.post(
        "/api/v1/workspaces/",
        json={"name": "Analytics Test"},
    )
    ws_id = resp.json()["id"]
    resp = await client.post(
        f"/api/v1/workspaces/{ws_id}/projects",
        json={"name": "Analytics Project"},
    )
    proj_id = resp.json()["id"]

    # Create snapshot
    resp = await client.post(
        f"/api/v1/analytics/projects/{proj_id}/snapshot"
    )
    assert resp.status_code == 200
    assert "score" in resp.json()
