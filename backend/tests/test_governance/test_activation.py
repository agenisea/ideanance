"""Tests for policy activation, suggestions, and plugin discovery."""

from httpx import AsyncClient

from modules.governance.constants import (
    CATEGORY_GOVERN,
    CATEGORY_MANAGE,
    CATEGORY_MAP,
    CATEGORY_MEASURE,
    FRAMEWORK_ID_NIST_AI_RMF,
    FRAMEWORK_NIST_AI_RMF,
    NIST_GOVERN_1_1,
    NIST_POLICY_COUNT,
)
from modules.governance.plugins import discover_plugins
from modules.governance.plugins.base import PolicyRuleProvider
from modules.governance.plugins.nist_ai_rmf import NistAiRmfPlugin
from modules.governance.suggestions import EvalSuggestionEngine


def test_nist_plugin_implements_policy_rule_provider():
    plugin = NistAiRmfPlugin()
    assert isinstance(plugin, PolicyRuleProvider)
    assert plugin.name == FRAMEWORK_NIST_AI_RMF
    assert plugin.framework == FRAMEWORK_NIST_AI_RMF
    rules = plugin.get_policy_rules()
    assert len(rules) >= NIST_POLICY_COUNT * 2  # 20 policies * ~2+ rules each


def test_plugin_discovery_finds_nist():
    plugins = discover_plugins()
    assert FRAMEWORK_NIST_AI_RMF in plugins
    assert isinstance(plugins[FRAMEWORK_NIST_AI_RMF], PolicyRuleProvider)


def test_suggestion_engine_generates_from_policies():
    """EvalSuggestionEngine is stateless — works on model objects."""
    # Create a mock policy-like object with rules containing eval_suggestions
    from unittest.mock import MagicMock

    policy = MagicMock()
    policy.id = "db-id-123"
    policy.policy_id = NIST_GOVERN_1_1
    policy.framework = FRAMEWORK_NIST_AI_RMF
    policy.rules = {
        "eval_suggestions": [
            {
                "criterion": "Purpose present",
                "metric": "purpose_present",
                "threshold": "boolean: true",
            },
            {
                "criterion": "Users listed",
                "metric": "users_listed",
                "threshold": "count >= 1",
            },
        ]
    }

    engine = EvalSuggestionEngine()
    suggestions = engine.suggest_from_policies([policy])
    assert len(suggestions) == 2
    assert suggestions[0].criterion_id == f"{NIST_GOVERN_1_1}-eval-001"
    assert suggestions[0].metric == "purpose_present"
    assert suggestions[1].criterion_id == f"{NIST_GOVERN_1_1}-eval-002"


async def test_activate_framework_via_api(client: AsyncClient):
    # Create workspace + project
    resp = await client.post(
        "/api/v1/workspaces/", json={"name": "Activation Test"}
    )
    ws_id = resp.json()["id"]
    resp = await client.post(
        f"/api/v1/workspaces/{ws_id}/projects",
        json={"name": "Test Project"},
    )
    proj_id = resp.json()["id"]

    # Activate NIST AI RMF
    resp = await client.post(
        f"/api/v1/governance/projects/{proj_id}/activate",
        json={"framework_id": FRAMEWORK_ID_NIST_AI_RMF},
    )
    assert resp.status_code == 200
    policies = resp.json()
    assert len(policies) == NIST_POLICY_COUNT

    # Verify all 4 categories present
    categories = {p["category"] for p in policies}
    assert categories == {
        CATEGORY_GOVERN,
        CATEGORY_MAP,
        CATEGORY_MEASURE,
        CATEGORY_MANAGE,
    }

    # Verify idempotent — activating again returns same 20
    resp = await client.post(
        f"/api/v1/governance/projects/{proj_id}/activate",
        json={"framework_id": FRAMEWORK_ID_NIST_AI_RMF},
    )
    assert len(resp.json()) == NIST_POLICY_COUNT


async def test_suggestions_endpoint(client: AsyncClient):
    # Setup: workspace + project + activate
    resp = await client.post(
        "/api/v1/workspaces/", json={"name": "Suggestions Test"}
    )
    ws_id = resp.json()["id"]
    resp = await client.post(
        f"/api/v1/workspaces/{ws_id}/projects",
        json={"name": "Test Project"},
    )
    proj_id = resp.json()["id"]
    await client.post(
        f"/api/v1/governance/projects/{proj_id}/activate",
        json={"framework_id": FRAMEWORK_ID_NIST_AI_RMF},
    )

    # Get suggestions
    resp = await client.get(
        f"/api/v1/governance/projects/{proj_id}/suggestions"
    )
    assert resp.status_code == 200
    suggestions = resp.json()
    # 20 policies * ~2 suggestions each = ~40+
    assert len(suggestions) >= NIST_POLICY_COUNT * 2
    assert suggestions[0]["framework"] == FRAMEWORK_NIST_AI_RMF
    assert "metric" in suggestions[0]


async def test_plugins_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/governance/plugins")
    assert resp.status_code == 200
    plugins = resp.json()
    assert len(plugins) >= 1
    nist = next(p for p in plugins if p["framework"] == FRAMEWORK_NIST_AI_RMF)
    assert nist["name"] == FRAMEWORK_NIST_AI_RMF
