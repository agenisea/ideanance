"""Agent pipeline orchestrator.

Router -> Fence -> Handoff -> Agent -> Gov Filter -> Cost Track.
Cross-cutting concerns live here, not in BaseIdeananceAgent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import structlog
from pydantic import BaseModel

from core.handoff.constants import HandoffStatus
from core.handoff.protocols import HandoffManagerProtocol
from core.handoff.schema import HandoffRequest
from core.observability.costs import TokenUsage
from core.observability.protocols import (
    CostAggregatorProtocol,
    KillSwitchProtocol,
)
from core.security.sanitization import fence_user_content
from modules.agents.base import (
    AgentRunMetadata,
    BaseIdeananceAgent,
)
from modules.agents.deps import GovernanceDeps, RouterDeps
from modules.agents.governance_filter import (
    GovernanceFilter,
    GovernanceFilterOutput,
)
from modules.agents.query_router import (
    QueryRouter,
    RouteDecision,
    TaskType,
)

log = structlog.get_logger()


@dataclass
class PipelineResult:
    """Result of a full pipeline execution."""

    output: BaseModel | None = None
    governance: GovernanceFilterOutput | None = None
    metadata: AgentRunMetadata | None = None
    route: RouteDecision | None = None
    warning: str | None = None
    needs_clarification: bool = False
    clarification_message: str = ""


class AgentPipeline:
    """Orchestrates: Router -> Fence -> Handoff -> Agent -> Filter.

    Cross-cutting concerns (fencing, cost tracking, kill switches)
    live on the pipeline, not inside individual agents (SRP).
    """

    def __init__(
        self,
        router: QueryRouter,
        agents: dict[str, BaseIdeananceAgent[Any]],
        gov_filter: GovernanceFilter,
        handoff_manager: HandoffManagerProtocol | None = None,
        cost_aggregator: CostAggregatorProtocol | None = None,
        kill_switches: KillSwitchProtocol | None = None,
    ) -> None:
        self.router = router
        self.agents = agents
        self.gov_filter = gov_filter
        self.handoff_manager = handoff_manager
        self.cost_aggregator = cost_aggregator
        self.kill_switches = kill_switches

    async def execute(
        self,
        prompt: str,
        governance_deps: GovernanceDeps,
        router_deps: RouterDeps | None = None,
        *,
        request_id: str = "",
    ) -> PipelineResult:
        """Execute the full pipeline with resilience."""
        # Content fencing at pipeline boundary
        fenced_prompt = fence_user_content(prompt)

        # 1. Route
        if router_deps is None:
            router_deps = RouterDeps(
                workspace_id=governance_deps.workspace_id,
                project_id=governance_deps.project_id,
                available_agents=list(self.agents.keys()),
            )

        route, route_meta = await self.router.run(
            fenced_prompt, deps=router_deps
        )

        # 2. Check for clarification
        if route.task_type == TaskType.CLARIFICATION:
            return PipelineResult(
                route=route,
                needs_clarification=True,
                clarification_message=route.reasoning,
            )

        # 3. Kill switch check
        if self.kill_switches and not self.kill_switches.is_agent_enabled(
            route.target_agent
        ):
            log.warning(
                "pipeline.agent_disabled",
                agent=route.target_agent,
            )
            return PipelineResult(
                route=route,
                warning=f"Agent '{route.target_agent}' disabled",
                needs_clarification=True,
                clarification_message=(
                    "This agent is temporarily unavailable."
                ),
            )

        # 4. Resolve target agent
        agent = self.agents.get(route.target_agent)
        if agent is None:
            return PipelineResult(
                route=route,
                needs_clarification=True,
                clarification_message=(
                    f"Unknown agent: {route.target_agent}"
                ),
            )

        # 5. Handoff protocol (if manager available)
        if self.handoff_manager:
            handoff_request = HandoffRequest(
                trace_id=request_id or str(uuid4()),
                source_agent=self.router.id,
                handoff_to=route.target_agent,
                reason=route.reasoning,
                context_for_target={"prompt": prompt},
            )
            handoff_response = (
                await self.handoff_manager.process_handoff(
                    handoff_request
                )
            )
            if handoff_response.status == HandoffStatus.FAILED:
                return PipelineResult(
                    route=route,
                    warning=handoff_response.failure_reason,
                    needs_clarification=True,
                    clarification_message=(
                        handoff_response.failure_reason or ""
                    ),
                )

        # 6. Dispatch to domain agent
        result, metadata = await agent.run(
            fenced_prompt, deps=governance_deps
        )

        # 7. Governance filter
        gov_result = self.gov_filter.check(result)

        # 8. Degradation warning
        warning = self.gov_filter.add_degradation_warning(metadata)

        # 9. Cost tracking (post-execution)
        self._track_cost(metadata, request_id)

        return PipelineResult(
            output=result,
            governance=gov_result,
            metadata=metadata,
            route=route,
            warning=warning,
        )

    def _track_cost(
        self,
        metadata: AgentRunMetadata | None,
        request_id: str,
    ) -> None:
        """Track cost and trigger kill switch if over limit."""
        if not self.cost_aggregator or not metadata:
            return

        usage = TokenUsage(
            prompt_tokens=metadata.token_usage.get("input", 0),
            completion_tokens=metadata.token_usage.get(
                "output", 0
            ),
            model=metadata.model_used,
        )
        self.cost_aggregator.add_usage(request_id, usage)

        if (
            self.cost_aggregator.is_over_daily_limit()
            and self.kill_switches
        ):
            self.kill_switches.disable_all_agents(
                "Daily cost limit exceeded"
            )
            log.warning(
                "pipeline.daily_cost_exceeded",
                request_id=request_id,
            )
