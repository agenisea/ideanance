"""End-to-end API test: create a Governance-Wired Project through HTTP endpoints."""

from httpx import AsyncClient

from modules.governance.constants import (
    CATEGORY_GOVERN,
    FRAMEWORK_NIST_AI_RMF,
    NIST_GOVERN_1_1,
)


async def test_create_governance_wiring_via_api(client: AsyncClient):
    # 1. Create workspace
    resp = await client.post("/api/v1/workspaces/", json={"name": "Test"})
    assert resp.status_code == 201
    ws_id = resp.json()["id"]

    # 2. Create project
    resp = await client.post(
        f"/api/v1/workspaces/{ws_id}/projects",
        json={"name": "Test Project"},
    )
    assert resp.status_code == 201
    proj_id = resp.json()["id"]

    # 3. Add governance policy
    resp = await client.post(
        f"/api/v1/governance/projects/{proj_id}/policies",
        json={
            "framework": FRAMEWORK_NIST_AI_RMF,
            "policy_id": NIST_GOVERN_1_1,
            "name": "Legal Requirements",
            "category": CATEGORY_GOVERN,
            "severity": "error",
            "rules": {
                "rules": [
                    {
                        "check": "field_present",
                        "target": "design.purpose",
                        "message": "Need purpose",
                    }
                ]
            },
        },
    )
    assert resp.status_code == 201
    policy_id = resp.json()["id"]

    # 4. Create evaluation + criterion
    resp = await client.post(
        f"/api/v1/evaluations/projects/{proj_id}/evaluations",
        json={"name": "Compliance Evals"},
    )
    assert resp.status_code == 201
    eval_id = resp.json()["id"]

    resp = await client.post(
        f"/api/v1/evaluations/{eval_id}/criteria",
        json={
            "criterion_id": "eval-001",
            "description": "Purpose statement check",
            "metric": "purpose_present",
            "threshold": "true",
        },
    )
    assert resp.status_code == 201
    crit_id = resp.json()["id"]

    # 5. Wire policy to criterion — THE CORE OPERATION
    resp = await client.post(
        f"/api/v1/governance/projects/{proj_id}/wirings",
        json={
            "policy_id": policy_id,
            "criterion_id": crit_id,
            "rationale": "GOVERN-1.1 maps to purpose eval",
        },
    )
    assert resp.status_code == 201
    wiring = resp.json()
    assert wiring["policy_id"] == policy_id
    assert wiring["criterion_id"] == crit_id

    # 6. Verify wiring exists
    resp = await client.get(f"/api/v1/governance/projects/{proj_id}/wirings")
    assert resp.status_code == 200
    wirings = resp.json()
    assert len(wirings) == 1


async def test_governance_check_via_api(client: AsyncClient):
    # Setup: workspace + project + policy
    resp = await client.post("/api/v1/workspaces/", json={"name": "WS"})
    ws_id = resp.json()["id"]
    resp = await client.post(
        f"/api/v1/workspaces/{ws_id}/projects", json={"name": "Proj"}
    )
    proj_id = resp.json()["id"]
    await client.post(
        f"/api/v1/governance/projects/{proj_id}/policies",
        json={
            "framework": FRAMEWORK_NIST_AI_RMF,
            "policy_id": NIST_GOVERN_1_1,
            "name": "Legal Reqs",
            "category": CATEGORY_GOVERN,
            "rules": {
                "rules": [
                    {
                        "check": "field_present",
                        "target": "design.purpose",
                        "message": "Need purpose",
                    }
                ]
            },
        },
    )

    # Run check with purpose present -> should pass
    resp = await client.post(
        "/api/v1/governance/check",
        json={
            "project_id": proj_id,
            "design_content": {"design": {"purpose": "Help users"}},
        },
    )
    assert resp.status_code == 200
    assert resp.json()["overall_score"] == 1.0

    # Run check without purpose -> should fail
    resp = await client.post(
        "/api/v1/governance/check",
        json={
            "project_id": proj_id,
            "design_content": {"design": {}},
        },
    )
    assert resp.status_code == 200
    assert resp.json()["overall_score"] == 0.0
