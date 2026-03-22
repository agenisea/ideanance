"""Schemas for agent topology governance."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentNode:
    """An agent in the topology graph."""

    agent_id: str
    agent_type: str  # "router" | "domain" | "filter"
    model: str
    design_content: dict = field(default_factory=dict)
    delegations: list[str] = field(default_factory=list)
    governance_score: float = 0.0


@dataclass
class AgentGovernanceResult:
    """Governance evaluation result for a single agent."""

    agent_id: str
    agent_type: str
    governance_score: float
    policy_results: list[dict] = field(default_factory=list)


@dataclass
class GovernanceBottleneck:
    """An agent that drags down pipeline governance score."""

    agent_id: str
    score: float
    recommendation: str = ""


@dataclass
class TopologyGovernanceResult:
    """Complete governance evaluation for an agent topology."""

    pipeline_score: float
    agent_results: list[AgentGovernanceResult]
    bottlenecks: list[GovernanceBottleneck]
    delegation_depth: int
    has_circular_delegation: bool
