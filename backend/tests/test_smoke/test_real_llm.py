"""Real LLM smoke test — run manually before deployment.

Skipped in CI (requires ANTHROPIC_API_KEY).
Run with: ANTHROPIC_API_KEY=sk-ant-... uv run pytest tests/test_smoke/ -v
"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="Real API key required — run manually",
)


async def test_health_endpoint_works(client):
    """Health endpoint responds."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] in ("healthy", "degraded")


async def test_governance_check_with_real_data(client):
    """Governance check against NIST with real policies."""
    # Create workspace + project
    resp = await client.post(
        "/api/v1/workspaces/",
        json={"name": "Smoke Test"},
    )
    assert resp.status_code == 201
    ws_id = resp.json()["id"]

    resp = await client.post(
        f"/api/v1/workspaces/{ws_id}/projects",
        json={"name": "Smoke Project"},
    )
    assert resp.status_code == 201
    proj_id = resp.json()["id"]

    # Activate NIST AI RMF
    resp = await client.post(
        f"/api/v1/governance/projects/{proj_id}/activate",
        json={"framework_id": "nist-ai-rmf"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 20

    # Run governance check
    resp = await client.post(
        "/api/v1/governance/check",
        json={
            "project_id": proj_id,
            "design_content": {
                "design": {
                    "purpose": "AI medical triage",
                    "intended_users": "Clinicians",
                    "risk_assessment": (
                        "High risk with patient safety"
                        " implications"
                    ),
                }
            },
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_score" in data
    assert len(data["results"]) > 0


async def test_analytics_north_star(client):
    """North Star metric endpoint works."""
    resp = await client.get(
        "/api/v1/analytics/north-star"
    )
    assert resp.status_code == 200
    assert (
        "governance_wired_projects" in resp.json()
    )
