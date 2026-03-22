"""Tests for topology governance — PLAN35."""

from modules.agents.topology import (
    TopologyGovernanceService,
    compute_delegation_depth,
    compute_pipeline_score,
    detect_circular_delegation,
    identify_governance_bottlenecks,
)
from modules.agents.topology_schemas import (
    AgentGovernanceResult,
    AgentNode,
)
from modules.governance.engine import GovernanceEngine, PolicyRule

# --- Pure function tests ---


def test_pipeline_score_weakest_link():
    results = [
        AgentGovernanceResult("router", "router", 0.92),
        AgentGovernanceResult("advisor", "domain", 0.78),
        AgentGovernanceResult("interpreter", "domain", 0.85),
    ]
    assert compute_pipeline_score(results) == 0.78


def test_pipeline_score_empty():
    assert compute_pipeline_score([]) == 0.0


def test_pipeline_score_all_perfect():
    results = [
        AgentGovernanceResult("a", "domain", 1.0),
        AgentGovernanceResult("b", "domain", 1.0),
    ]
    assert compute_pipeline_score(results) == 1.0


def test_bottlenecks_below_threshold():
    results = [
        AgentGovernanceResult("router", "router", 0.92),
        AgentGovernanceResult("advisor", "domain", 0.65),
        AgentGovernanceResult("generator", "domain", 0.91),
    ]
    bottlenecks = identify_governance_bottlenecks(results, threshold=0.8)
    assert len(bottlenecks) == 1
    assert bottlenecks[0].agent_id == "advisor"
    assert bottlenecks[0].score == 0.65


def test_no_bottlenecks():
    results = [
        AgentGovernanceResult("a", "domain", 0.95),
        AgentGovernanceResult("b", "domain", 0.88),
    ]
    bottlenecks = identify_governance_bottlenecks(results, threshold=0.8)
    assert len(bottlenecks) == 0


def test_detect_no_circular():
    topology = [
        AgentNode("router", "router", "haiku", delegations=["advisor", "interpreter"]),
        AgentNode("advisor", "domain", "sonnet", delegations=[]),
        AgentNode("interpreter", "domain", "sonnet", delegations=["generator"]),
        AgentNode("generator", "domain", "sonnet", delegations=[]),
    ]
    assert detect_circular_delegation(topology) is False


def test_detect_circular():
    topology = [
        AgentNode("a", "domain", "sonnet", delegations=["b"]),
        AgentNode("b", "domain", "sonnet", delegations=["c"]),
        AgentNode("c", "domain", "sonnet", delegations=["a"]),  # Circular!
    ]
    assert detect_circular_delegation(topology) is True


def test_delegation_depth_linear():
    topology = [
        AgentNode("router", "router", "haiku", delegations=["advisor"]),
        AgentNode("advisor", "domain", "sonnet", delegations=["generator"]),
        AgentNode("generator", "domain", "sonnet", delegations=["formatter"]),
        AgentNode("formatter", "domain", "sonnet", delegations=[]),
    ]
    assert compute_delegation_depth(topology) == 4


def test_delegation_depth_flat():
    topology = [
        AgentNode("router", "router", "haiku", delegations=["a", "b", "c"]),
        AgentNode("a", "domain", "sonnet", delegations=[]),
        AgentNode("b", "domain", "sonnet", delegations=[]),
        AgentNode("c", "domain", "sonnet", delegations=[]),
    ]
    assert compute_delegation_depth(topology) == 2


def test_delegation_depth_single():
    topology = [AgentNode("solo", "domain", "sonnet", delegations=[])]
    assert compute_delegation_depth(topology) == 1


# --- Service tests ---


def _make_topology() -> list[AgentNode]:
    return [
        AgentNode(
            "router", "router", "haiku",
            governance_score=0.92,
            delegations=["advisor", "interpreter"],
        ),
        AgentNode(
            "advisor", "domain", "sonnet",
            governance_score=0.78,
            delegations=[],
        ),
        AgentNode(
            "interpreter", "domain", "sonnet",
            governance_score=0.85,
            delegations=["generator"],
        ),
        AgentNode(
            "generator", "domain", "sonnet",
            governance_score=0.91,
            delegations=["formatter"],
        ),
        AgentNode(
            "formatter", "domain", "sonnet",
            governance_score=0.88,
            delegations=[],
        ),
    ]


def test_service_evaluate_topology():
    svc = TopologyGovernanceService(engine=GovernanceEngine())
    topology = _make_topology()
    result = svc.evaluate_topology(topology)

    assert result.pipeline_score == 0.78
    assert len(result.agent_results) == 5
    assert result.has_circular_delegation is False
    assert result.delegation_depth == 4


def test_service_finds_bottleneck():
    svc = TopologyGovernanceService(engine=GovernanceEngine())
    topology = _make_topology()
    result = svc.evaluate_topology(topology)

    assert len(result.bottlenecks) == 1
    assert result.bottlenecks[0].agent_id == "advisor"


def test_service_with_policy_evaluation():
    svc = TopologyGovernanceService(engine=GovernanceEngine())
    topology = [
        AgentNode(
            "agent-1", "domain", "sonnet",
            design_content={"design": {"purpose": "Test agent"}},
            delegations=[],
        ),
    ]
    policies_per_agent = {
        "agent-1": [
            PolicyRule(
                check="field_present",
                target="design.purpose",
                message="Must have purpose",
            ),
        ],
    }
    result = svc.evaluate_topology(topology, policies_per_agent)
    assert result.agent_results[0].governance_score == 1.0


def test_service_with_failing_policy():
    svc = TopologyGovernanceService(engine=GovernanceEngine())
    topology = [
        AgentNode(
            "agent-1", "domain", "sonnet",
            design_content={"design": {}},  # Missing purpose
            delegations=[],
        ),
    ]
    policies_per_agent = {
        "agent-1": [
            PolicyRule(
                check="field_present",
                target="design.purpose",
                message="Must have purpose",
            ),
        ],
    }
    result = svc.evaluate_topology(topology, policies_per_agent)
    assert result.agent_results[0].governance_score == 0.0
    assert result.pipeline_score == 0.0


def test_service_circular_detection():
    svc = TopologyGovernanceService(engine=GovernanceEngine())
    topology = [
        AgentNode("a", "domain", "sonnet", governance_score=0.9, delegations=["b"]),
        AgentNode("b", "domain", "sonnet", governance_score=0.9, delegations=["a"]),
    ]
    result = svc.evaluate_topology(topology)
    assert result.has_circular_delegation is True
