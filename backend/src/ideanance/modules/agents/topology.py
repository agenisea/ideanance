"""Topology governance service — evaluates governance across agent topologies.

Pure computation, not persisted state. Results computed on-demand.
"""

from __future__ import annotations

import structlog

from ideanance.modules.agents.topology_schemas import (
    AgentGovernanceResult,
    AgentNode,
    GovernanceBottleneck,
    TopologyGovernanceResult,
)
from ideanance.modules.governance.engine import GovernanceEngine, PolicyRule

log = structlog.get_logger()

# Default threshold below which an agent is a bottleneck
DEFAULT_BOTTLENECK_THRESHOLD = 0.8


# --- Pure functions (independently testable) ---


def compute_pipeline_score(
    agent_results: list[AgentGovernanceResult],
) -> float:
    """Pipeline score = minimum agent score (weakest link). Pure function."""
    if not agent_results:
        return 0.0
    return min(r.governance_score for r in agent_results)


def identify_governance_bottlenecks(
    agent_results: list[AgentGovernanceResult],
    threshold: float = DEFAULT_BOTTLENECK_THRESHOLD,
) -> list[GovernanceBottleneck]:
    """Find agents below threshold. Pure function."""
    return [
        GovernanceBottleneck(
            agent_id=r.agent_id,
            score=r.governance_score,
            recommendation=(
                f"Agent '{r.agent_id}' scores {r.governance_score:.2f}, "
                f"below threshold {threshold:.2f}. "
                "Review governance compliance for this agent."
            ),
        )
        for r in agent_results
        if r.governance_score < threshold
    ]


def detect_circular_delegation(
    topology: list[AgentNode],
) -> bool:
    """Detect circular delegation in topology. Pure function."""
    adjacency: dict[str, list[str]] = {
        node.agent_id: node.delegations for node in topology
    }

    visited: set[str] = set()
    in_stack: set[str] = set()

    def _has_cycle(node_id: str) -> bool:
        if node_id in in_stack:
            return True
        if node_id in visited:
            return False
        visited.add(node_id)
        in_stack.add(node_id)
        for neighbor in adjacency.get(node_id, []):
            if _has_cycle(neighbor):
                return True
        in_stack.discard(node_id)
        return False

    return any(_has_cycle(node.agent_id) for node in topology)


def compute_delegation_depth(
    topology: list[AgentNode],
) -> int:
    """Compute maximum delegation depth. Pure function."""
    adjacency: dict[str, list[str]] = {
        node.agent_id: node.delegations for node in topology
    }
    all_targets = {d for node in topology for d in node.delegations}
    roots = [
        node.agent_id for node in topology if node.agent_id not in all_targets
    ]

    if not roots:
        return len(topology)  # Circular or no clear root

    def _depth(node_id: str, seen: set[str]) -> int:
        if node_id in seen:
            return 0
        seen.add(node_id)
        children = adjacency.get(node_id, [])
        if not children:
            return 1
        return 1 + max(_depth(c, seen) for c in children)

    return max(_depth(r, set()) for r in roots) if roots else 0


# --- Service class ---


class TopologyGovernanceService:
    """Evaluates governance across an agent topology.

    Pure computation — no database tables owned.
    """

    def __init__(self, engine: GovernanceEngine) -> None:
        self._engine = engine

    def evaluate_topology(
        self,
        topology: list[AgentNode],
        policies_per_agent: dict[str, list[PolicyRule]] | None = None,
    ) -> TopologyGovernanceResult:
        """Evaluate governance for entire agent topology."""
        log.info(
            "topology.evaluating",
            agent_count=len(topology),
        )
        agent_results: list[AgentGovernanceResult] = []

        for node in topology:
            if policies_per_agent and node.agent_id in policies_per_agent:
                rules = policies_per_agent[node.agent_id]
                check_results = self._engine.evaluate(
                    node.design_content, rules
                )
                score = self._engine.compute_score(check_results)
            else:
                score = node.governance_score

            agent_results.append(
                AgentGovernanceResult(
                    agent_id=node.agent_id,
                    agent_type=node.agent_type,
                    governance_score=score,
                )
            )

        pipeline_score = compute_pipeline_score(agent_results)
        bottlenecks = identify_governance_bottlenecks(agent_results)
        has_circular = detect_circular_delegation(topology)
        depth = compute_delegation_depth(topology)

        return TopologyGovernanceResult(
            pipeline_score=pipeline_score,
            agent_results=agent_results,
            bottlenecks=bottlenecks,
            delegation_depth=depth,
            has_circular_delegation=has_circular,
        )
