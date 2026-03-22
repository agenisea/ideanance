"""E2E: analytics snapshot + North Star — PLAN50."""

from httpx import AsyncClient

from ideanance.modules.governance.constants import (
    FRAMEWORK_ID_NIST_AI_RMF,
)


async def test_analytics_snapshot_flow(
    client: AsyncClient,
):
    """Create project → activate → snapshot → verify."""
    # Setup
    resp = await client.post(
        "/api/v1/workspaces/",
        json={"name": "Analytics E2E"},
    )
    ws_id = resp.json()["id"]
    resp = await client.post(
        f"/api/v1/workspaces/{ws_id}/projects",
        json={"name": "Analytics Project"},
    )
    proj_id = resp.json()["id"]

    # Activate NIST
    resp = await client.post(
        f"/api/v1/governance/projects/{proj_id}/activate",
        json={
            "framework_id": FRAMEWORK_ID_NIST_AI_RMF
        },
    )
    assert resp.status_code == 200

    # Create snapshot
    resp = await client.post(
        f"/api/v1/analytics/projects/{proj_id}/snapshot"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["policies_active"] > 0
    assert data["frameworks_active"] >= 1

    # Get score
    resp = await client.get(
        f"/api/v1/analytics/projects/{proj_id}/score"
    )
    assert resp.status_code == 200

    # Get coverage
    resp = await client.get(
        f"/api/v1/analytics/projects/{proj_id}/coverage"
    )
    assert resp.status_code == 200
