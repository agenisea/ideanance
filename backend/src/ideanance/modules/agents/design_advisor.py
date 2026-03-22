"""Design Advisor agent — analyzes designs against governance policies.

Uses Claude Sonnet 4.6. Streams responses. Tools use Protocol-typed repos.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from ideanance.modules.agents import (
    AGENT_IDS,
    MODELS,
    POLICY_SEARCH_LIMIT,
    TIMEOUTS_MS,
    TOKEN_BUDGETS,
)
from ideanance.modules.agents.base import AgentConfig, BaseIdeananceAgent
from ideanance.modules.agents.deps import GovernanceDeps


class GovernanceCitation(BaseModel):
    framework: str
    section_id: str
    section_title: str
    relevance: str


class GovernanceGap(BaseModel):
    description: str
    severity: str = Field(description="error | warning | info")
    citation: GovernanceCitation


class DesignAdvice(BaseModel):
    """Structured output from the Design Advisor."""

    suggestions: list[str]
    governance_gaps: list[GovernanceGap]
    governance_score: float = Field(ge=0.0, le=1.0)
    references: list[GovernanceCitation]


ADVISOR_CONFIG = AgentConfig(
    agent_id=AGENT_IDS["DESIGN_ADVISOR"],
    primary_model=MODELS["DOMAIN"],
    token_budget_in=TOKEN_BUDGETS["design_advisor"]["in"],
    token_budget_out=TOKEN_BUDGETS["design_advisor"]["out"],
    timeout_ms=TIMEOUTS_MS["design_advisor"],
    streaming=True,
)


class DesignAdvisor(BaseIdeananceAgent[DesignAdvice, GovernanceDeps]):
    def __init__(self, config: AgentConfig | None = None) -> None:
        super().__init__(config or ADVISOR_CONFIG)

    def _create_agent(self) -> Agent[Any, Any]:
        agent: Agent[GovernanceDeps, DesignAdvice] = Agent(
            model=self._build_model(),
            output_type=DesignAdvice,
            deps_type=GovernanceDeps,
            output_retries=self.config.max_retries,
            instructions=(
                "You are the Design Advisor for Ideanance.\n\n"
                "Your job: analyze agent designs against activated "
                "governance policies and suggest improvements with "
                "specific citations.\n\n"
                "Rules:\n"
                "- Every finding must cite a specific governance "
                "framework section.\n"
                "- Never hallucinate policies or section IDs.\n"
                "- Suggest concrete fixes, not generic recommendations.\n"
            ),
        )

        @agent.tool
        async def search_governance_policies(
            ctx: RunContext[GovernanceDeps], query: str
        ) -> str:
            """Search active governance policies by keyword."""
            policies = ctx.deps.active_policies
            matches = [
                p
                for p in policies
                if query.lower() in json.dumps(p).lower()
            ]
            return json.dumps(matches[:POLICY_SEARCH_LIMIT], default=str)

        @agent.tool
        async def get_project_agents(
            ctx: RunContext[GovernanceDeps],
        ) -> str:
            """Get all agent specs in the project."""
            return json.dumps(ctx.deps.agent_specs, default=str)

        return agent

    def _build_fallback(self) -> DesignAdvice:
        return DesignAdvice(
            suggestions=[
                "Unable to analyze design at this time. Please try again."
            ],
            governance_gaps=[],
            governance_score=0.0,
            references=[],
        )
