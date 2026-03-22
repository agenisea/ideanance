"""E2E test: multi-framework governance loop — PLAN40."""

from httpx import AsyncClient

from ideanance.modules.governance.constants import (
    EU_POLICY_COUNT,
    FRAMEWORK_EU_AI_ACT,
    FRAMEWORK_ID_EU_AI_ACT,
    FRAMEWORK_ID_NIST_AI_RMF,
    FRAMEWORK_NIST_AI_RMF,
    NIST_POLICY_COUNT,
)


async def test_multi_framework_governance_loop(client: AsyncClient):
    """Full governance loop: create → activate NIST + EU AI Act → check → export."""
    # 1. Create workspace + project
    resp = await client.post(
        "/api/v1/workspaces/", json={"name": "E2E Multi-Framework"}
    )
    assert resp.status_code == 201
    ws_id = resp.json()["id"]

    resp = await client.post(
        f"/api/v1/workspaces/{ws_id}/projects",
        json={"name": "E2E Project"},
    )
    assert resp.status_code == 201
    proj_id = resp.json()["id"]

    # 2. Activate NIST AI RMF
    resp = await client.post(
        f"/api/v1/governance/projects/{proj_id}/activate",
        json={"framework_id": FRAMEWORK_ID_NIST_AI_RMF},
    )
    assert resp.status_code == 200
    nist_policies = resp.json()
    assert len(nist_policies) == NIST_POLICY_COUNT

    # 3. Activate EU AI Act
    resp = await client.post(
        f"/api/v1/governance/projects/{proj_id}/activate",
        json={"framework_id": FRAMEWORK_ID_EU_AI_ACT},
    )
    assert resp.status_code == 200
    eu_policies = resp.json()
    assert len(eu_policies) == EU_POLICY_COUNT

    # 4. Verify all policies active
    resp = await client.get(
        f"/api/v1/governance/projects/{proj_id}/policies"
    )
    assert resp.status_code == 200
    all_policies = resp.json()
    assert len(all_policies) == NIST_POLICY_COUNT + EU_POLICY_COUNT
    frameworks = {p["framework"] for p in all_policies}
    assert frameworks == {FRAMEWORK_NIST_AI_RMF, FRAMEWORK_EU_AI_ACT}

    # 5. Run governance check
    resp = await client.post(
        "/api/v1/governance/check",
        json={
            "project_id": proj_id,
            "design_content": {
                "design": {
                    "purpose": "AI-powered customer support agent",
                    "intended_users": "Support team leads",
                    "risk_assessment": "Medium risk — handles sensitive customer data",
                }
            },
        },
    )
    assert resp.status_code == 200
    check_result = resp.json()
    assert "overall_score" in check_result
    assert len(check_result["results"]) > 0

    # 6. Get suggestions (should include both frameworks)
    resp = await client.get(
        f"/api/v1/governance/projects/{proj_id}/suggestions"
    )
    assert resp.status_code == 200
    suggestions = resp.json()
    suggestion_frameworks = {s["framework"] for s in suggestions}
    assert FRAMEWORK_NIST_AI_RMF in suggestion_frameworks
    assert FRAMEWORK_EU_AI_ACT in suggestion_frameworks

    # 7. Verify plugins endpoint shows both
    resp = await client.get("/api/v1/governance/plugins")
    assert resp.status_code == 200
    plugins = resp.json()
    plugin_frameworks = {p["framework"] for p in plugins}
    assert FRAMEWORK_NIST_AI_RMF in plugin_frameworks
    assert FRAMEWORK_EU_AI_ACT in plugin_frameworks
