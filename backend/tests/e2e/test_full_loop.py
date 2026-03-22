"""End-to-end smoke test: fresh project through full loop to handoff.

Proves the Milestone 6 success criteria:
"A user can complete the full loop: create project -> activate policies ->
 run governance check -> export handoff package"
"""


import pytest

from modules.governance.constants import (
    FRAMEWORK_ID_NIST_AI_RMF,
    NIST_POLICY_COUNT,
    SEVERITY_REQUIRED,
)


@pytest.mark.asyncio
async def test_full_governance_wired_project_loop(client):
    """Full loop: workspace -> project -> policies -> check -> wirings -> export."""
    # 1. Create workspace
    resp = await client.post(
        "/api/v1/workspaces/",
        json={"name": "E2E Test Workspace"},
    )
    assert resp.status_code == 201
    workspace_id = resp.json()["id"]

    # 2. Create project
    resp = await client.post(
        f"/api/v1/workspaces/{workspace_id}/projects",
        json={"name": "E2E Agent Project"},
    )
    assert resp.status_code == 201
    project_id = resp.json()["id"]

    # 3. Activate NIST AI RMF policies
    resp = await client.post(
        f"/api/v1/governance/projects/{project_id}/activate",
        json={"framework_id": FRAMEWORK_ID_NIST_AI_RMF},
    )
    assert resp.status_code == 200
    policies = resp.json()
    assert len(policies) >= NIST_POLICY_COUNT

    # 4. Create a design
    resp = await client.post(
        f"/api/v1/designs/projects/{project_id}/designs",
        json={
            "name": "Customer Support Agent",
            "design_type": "agent",
            "content": {
                "design": {
                    "purpose": "Help customers with support queries",
                    "intended_users": ["customers", "support staff"],
                    "risk_assessment": (
                        "Medium risk - handles personal data, "
                        "requires privacy controls"
                    ),
                }
            },
        },
    )
    assert resp.status_code == 201

    # 5. Run governance check
    resp = await client.post(
        "/api/v1/governance/check",
        json={
            "project_id": project_id,
            "design_content": {
                "design": {
                    "purpose": "Help customers with support queries",
                    "intended_users": ["customers", "support staff"],
                    "risk_assessment": "Medium risk - handles personal data",
                }
            },
        },
    )
    assert resp.status_code == 200
    check = resp.json()
    assert check["overall_score"] > 0

    # 6. Get eval suggestions
    resp = await client.get(
        f"/api/v1/governance/projects/{project_id}/suggestions"
    )
    assert resp.status_code == 200
    suggestions = resp.json()
    assert len(suggestions) > 0

    # 7. Create an evaluation + criterion, then wire
    resp = await client.post(
        f"/api/v1/evaluations/projects/{project_id}/evaluations",
        json={"name": "Governance Eval"},
    )
    assert resp.status_code == 201
    eval_id = resp.json()["id"]

    resp = await client.post(
        f"/api/v1/evaluations/{eval_id}/criteria",
        json={
            "criterion_id": "eval-purpose-001",
            "description": "Agent must state its purpose clearly",
            "metric": "purpose_statement_present",
            "threshold": "100%",
            "priority": SEVERITY_REQUIRED,
        },
    )
    assert resp.status_code == 201
    criterion_db_id = resp.json()["id"]

    # 8. Wire a policy to criterion
    policy_db_id = policies[0]["id"]
    resp = await client.post(
        f"/api/v1/governance/projects/{project_id}/wirings",
        json={
            "policy_id": policy_db_id,
            "criterion_id": criterion_db_id,
            "wiring_type": "manual",
            "confidence": 0.95,
            "rationale": "Purpose statement required by governance",
        },
    )
    assert resp.status_code == 201, f"Wiring failed: {resp.json()}"

    # 9. Verify project is Governance-Wired (North Star!)
    resp = await client.get(
        f"/api/v1/governance/projects/{project_id}/wirings"
    )
    wirings = resp.json()
    assert len(wirings) > 0, "Project must be Governance-Wired"

    # 10. Preview export
    resp = await client.get(
        f"/api/v1/exports/projects/{project_id}/preview"
    )
    assert resp.status_code == 200
    preview = resp.json()
    assert preview["active_policy_count"] >= NIST_POLICY_COUNT
    assert preview["wiring_count"] == 1
    assert "ai-context.yml" in preview["artifact_filenames"]

    # 11. Download ZIP
    resp = await client.get(
        f"/api/v1/exports/projects/{project_id}/download"
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"
    assert len(resp.content) > 0
