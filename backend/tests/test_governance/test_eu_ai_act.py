"""Tests for EU AI Act governance framework — PLAN32."""

from pathlib import Path
from unittest.mock import MagicMock

from httpx import AsyncClient

from modules.governance.constants import (
    EU_CATEGORY_HIGH_RISK,
    EU_CATEGORY_LIMITED,
    EU_CATEGORY_PROHIBITED,
    EU_CATEGORY_TRANSPARENCY,
    EU_POLICY_COUNT,
    FRAMEWORK_EU_AI_ACT,
    FRAMEWORK_ID_EU_AI_ACT,
    FRAMEWORK_ID_NIST_AI_RMF,
    FRAMEWORK_NIST_AI_RMF,
    NIST_POLICY_COUNT,
)
from modules.governance.loader import (
    load_all_policies,
    load_framework_policies,
)
from modules.governance.plugins.base import PolicyRuleProvider
from modules.governance.plugins.eu_ai_act import EuAiActPlugin
from modules.governance.suggestions import EvalSuggestionEngine

EU_FIXTURES_DIR = (
    Path(__file__).resolve().parents[3] / "governance-policies" / "eu-ai-act"
)


def test_load_all_eu_ai_act_fixtures():
    policies = load_framework_policies(EU_FIXTURES_DIR)
    assert len(policies) == EU_POLICY_COUNT
    frameworks = {p.framework for p in policies}
    assert frameworks == {FRAMEWORK_EU_AI_ACT}


def test_eu_ai_act_has_all_categories():
    policies = load_framework_policies(EU_FIXTURES_DIR)
    categories = {p.category for p in policies}
    assert categories == {
        EU_CATEGORY_PROHIBITED,
        EU_CATEGORY_HIGH_RISK,
        EU_CATEGORY_LIMITED,
        EU_CATEGORY_TRANSPARENCY,
    }


def test_eu_ai_act_category_counts():
    policies = load_framework_policies(EU_FIXTURES_DIR)
    by_cat = {}
    for p in policies:
        by_cat.setdefault(p.category, []).append(p)
    assert len(by_cat[EU_CATEGORY_PROHIBITED]) == 4
    assert len(by_cat[EU_CATEGORY_HIGH_RISK]) == 12
    assert len(by_cat[EU_CATEGORY_LIMITED]) == 3
    assert len(by_cat[EU_CATEGORY_TRANSPARENCY]) == 2


def test_all_eu_policies_have_rules():
    policies = load_framework_policies(EU_FIXTURES_DIR)
    for p in policies:
        assert len(p.rules) >= 2, f"{p.id} has fewer than 2 rules"


def test_all_eu_policies_have_remediation():
    policies = load_framework_policies(EU_FIXTURES_DIR)
    for p in policies:
        assert "guidance" in p.remediation, (
            f"{p.id} missing remediation guidance"
        )


def test_all_eu_policies_have_eval_suggestions():
    policies = load_framework_policies(EU_FIXTURES_DIR)
    for p in policies:
        assert len(p.eval_suggestions) >= 1, (
            f"{p.id} missing eval_suggestions"
        )


def test_eu_plugin_implements_policy_rule_provider():
    plugin = EuAiActPlugin()
    assert isinstance(plugin, PolicyRuleProvider)
    assert plugin.name == FRAMEWORK_EU_AI_ACT
    assert plugin.framework == FRAMEWORK_EU_AI_ACT
    assert plugin.version == "2024/1689"
    rules = plugin.get_policy_rules()
    assert len(rules) >= EU_POLICY_COUNT * 2  # 20 policies * ~2+ rules each


def test_load_all_policies_includes_both_frameworks():
    all_policies = load_all_policies()
    frameworks = {p.framework for p in all_policies}
    assert FRAMEWORK_NIST_AI_RMF in frameworks
    assert FRAMEWORK_EU_AI_ACT in frameworks
    assert len(all_policies) >= NIST_POLICY_COUNT + EU_POLICY_COUNT


def test_suggestion_engine_works_with_eu_ai_act():
    policy = MagicMock()
    policy.id = "db-id-eu-1"
    policy.policy_id = "eu-art9-risk-management"
    policy.framework = FRAMEWORK_EU_AI_ACT
    policy.rules = {
        "eval_suggestions": [
            {
                "criterion": "Risk management system documented",
                "metric": "risk_management_plan_present",
                "threshold": "boolean: true",
            },
        ]
    }

    engine = EvalSuggestionEngine()
    suggestions = engine.suggest_from_policies([policy])
    assert len(suggestions) == 1
    assert suggestions[0].framework == FRAMEWORK_EU_AI_ACT
    assert suggestions[0].criterion_id == "eu-art9-risk-management-eval-001"


async def test_activate_eu_ai_act_via_api(client: AsyncClient):
    # Create workspace + project
    resp = await client.post(
        "/api/v1/workspaces/", json={"name": "EU AI Act Test"}
    )
    ws_id = resp.json()["id"]
    resp = await client.post(
        f"/api/v1/workspaces/{ws_id}/projects",
        json={"name": "EU Project"},
    )
    proj_id = resp.json()["id"]

    # Activate EU AI Act
    resp = await client.post(
        f"/api/v1/governance/projects/{proj_id}/activate",
        json={"framework_id": FRAMEWORK_ID_EU_AI_ACT},
    )
    assert resp.status_code == 200
    policies = resp.json()
    assert len(policies) == EU_POLICY_COUNT

    # Verify all categories present
    categories = {p["category"] for p in policies}
    assert categories == {
        EU_CATEGORY_PROHIBITED,
        EU_CATEGORY_HIGH_RISK,
        EU_CATEGORY_LIMITED,
        EU_CATEGORY_TRANSPARENCY,
    }


async def test_activate_both_frameworks_via_api(client: AsyncClient):
    # Create workspace + project
    resp = await client.post(
        "/api/v1/workspaces/", json={"name": "Multi-Framework Test"}
    )
    ws_id = resp.json()["id"]
    resp = await client.post(
        f"/api/v1/workspaces/{ws_id}/projects",
        json={"name": "Multi Project"},
    )
    proj_id = resp.json()["id"]

    # Activate NIST AI RMF
    resp = await client.post(
        f"/api/v1/governance/projects/{proj_id}/activate",
        json={"framework_id": FRAMEWORK_ID_NIST_AI_RMF},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == NIST_POLICY_COUNT

    # Activate EU AI Act
    resp = await client.post(
        f"/api/v1/governance/projects/{proj_id}/activate",
        json={"framework_id": FRAMEWORK_ID_EU_AI_ACT},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == EU_POLICY_COUNT

    # Get all active policies — should be NIST + EU combined
    resp = await client.get(
        f"/api/v1/governance/projects/{proj_id}/policies"
    )
    assert resp.status_code == 200
    all_policies = resp.json()
    assert len(all_policies) == NIST_POLICY_COUNT + EU_POLICY_COUNT
    frameworks = {p["framework"] for p in all_policies}
    assert frameworks == {FRAMEWORK_NIST_AI_RMF, FRAMEWORK_EU_AI_ACT}


async def test_plugin_discovery_finds_eu_ai_act(client: AsyncClient):
    resp = await client.get("/api/v1/governance/plugins")
    assert resp.status_code == 200
    plugins = resp.json()
    frameworks = {p["framework"] for p in plugins}
    assert FRAMEWORK_EU_AI_ACT in frameworks
    assert FRAMEWORK_NIST_AI_RMF in frameworks
