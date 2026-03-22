"""API integration tests for Phase 2 endpoints — PLAN42."""

from httpx import AsyncClient


async def test_integrations_promptfoo_config(
    client: AsyncClient,
):
    resp = await client.post(
        "/api/v1/integrations/promptfoo/config",
        json={
            "project_name": "Test Project",
            "criteria": [
                {
                    "criterion_id": "eval-1",
                    "description": "Purpose present",
                    "metric": "field_present",
                    "threshold": "true",
                    "governance_wiring": "nist-govern-1.1",
                }
            ],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "yaml" in data
    assert "Test Project" in data["yaml"]


async def test_integrations_promptfoo_results(
    client: AsyncClient,
):
    resp = await client.post(
        "/api/v1/integrations/promptfoo/results",
        json={
            "results": {
                "results": [
                    {
                        "success": True,
                        "score": 1.0,
                        "metadata": {
                            "ideanance_criterion_id": "e1",
                        },
                    },
                    {
                        "success": False,
                        "score": 0.0,
                        "metadata": {
                            "ideanance_criterion_id": "e2",
                        },
                    },
                ]
            }
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_tests"] == 2
    assert data["passed"] == 1
    assert data["failed"] == 1


async def test_integrations_ci_workflow(
    client: AsyncClient,
):
    resp = await client.post(
        "/api/v1/integrations/ci-workflow",
        json={
            "project_name": "My Agent",
            "frameworks": ["NIST AI RMF", "EU AI Act"],
            "pass_threshold": 95,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "yaml" in data
    assert "My Agent" in data["yaml"]
    assert "95" in data["yaml"]


async def test_topology_evaluate(client: AsyncClient):
    resp = await client.post(
        "/api/v1/topology/evaluate",
        json={
            "topology": [
                {
                    "agent_id": "router",
                    "agent_type": "router",
                    "model": "haiku",
                    "governance_score": 0.92,
                    "delegations": ["advisor"],
                },
                {
                    "agent_id": "advisor",
                    "agent_type": "domain",
                    "model": "sonnet",
                    "governance_score": 0.78,
                    "delegations": [],
                },
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["pipeline_score"] == 0.78
    assert data["agent_count"] == 2
    assert data["has_circular_delegation"] is False
    assert data["bottleneck_count"] == 1


async def test_topology_circular_detection(
    client: AsyncClient,
):
    resp = await client.post(
        "/api/v1/topology/evaluate",
        json={
            "topology": [
                {
                    "agent_id": "a",
                    "agent_type": "domain",
                    "model": "sonnet",
                    "governance_score": 0.9,
                    "delegations": ["b"],
                },
                {
                    "agent_id": "b",
                    "agent_type": "domain",
                    "model": "sonnet",
                    "governance_score": 0.9,
                    "delegations": ["a"],
                },
            ]
        },
    )
    assert resp.status_code == 200
    assert resp.json()["has_circular_delegation"] is True


async def test_composition_root_factories_exist():
    """Verify all Phase 2 factories are importable."""
    from dependencies import (
        get_ci_generator,
        get_composition_engine,
        get_context_assembler,
        get_custom_framework_service,
        get_hybrid_retriever,
        get_promptfoo_exporter,
        get_result_importer,
        get_topology_governance_service,
    )

    assert callable(get_composition_engine)
    assert callable(get_hybrid_retriever)
    assert callable(get_context_assembler)
    assert callable(get_topology_governance_service)
    assert callable(get_promptfoo_exporter)
    assert callable(get_result_importer)
    assert callable(get_ci_generator)
    assert callable(get_custom_framework_service)


def test_shared_governance_engine():
    """GovernanceEngine is shared, not duplicated."""
    from dependencies import _governance_engine
    from modules.governance.engine import (
        GovernanceEngine,
    )

    assert isinstance(_governance_engine, GovernanceEngine)
