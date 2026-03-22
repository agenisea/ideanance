"""Topology governance endpoints."""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dependencies import (
    get_topology_governance_service,
)
from modules.agents.topology import (
    TopologyGovernanceService,
)
from modules.agents.topology_schemas import AgentNode

router = APIRouter(
    prefix="/topology", tags=["topology"]
)


class AgentNodeRequest(BaseModel):
    agent_id: str
    agent_type: str
    model: str
    governance_score: float = 0.0
    delegations: list[str] = []


class TopologyEvaluateRequest(BaseModel):
    topology: list[AgentNodeRequest]


@router.post("/evaluate")
async def evaluate_topology(
    request: TopologyEvaluateRequest,
    svc: TopologyGovernanceService = Depends(
        get_topology_governance_service
    ),
) -> dict[str, Any]:
    nodes = [
        AgentNode(
            agent_id=n.agent_id,
            agent_type=n.agent_type,
            model=n.model,
            governance_score=n.governance_score,
            delegations=n.delegations,
        )
        for n in request.topology
    ]
    result = svc.evaluate_topology(nodes)
    return {
        "pipeline_score": result.pipeline_score,
        "delegation_depth": result.delegation_depth,
        "has_circular_delegation": (
            result.has_circular_delegation
        ),
        "agent_count": len(result.agent_results),
        "bottleneck_count": len(result.bottlenecks),
        "bottlenecks": [
            {
                "agent_id": b.agent_id,
                "score": b.score,
                "recommendation": b.recommendation,
            }
            for b in result.bottlenecks
        ],
    }
