"""Policy Interpreter agent — explains governance policies in plain language.

Uses Claude Sonnet 4.6. Streams responses. Tools use Protocol-typed repos.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from modules.agents import (
    AGENT_IDS,
    MODELS,
    POLICY_SEARCH_LIMIT,
    TIMEOUTS_MS,
    TOKEN_BUDGETS,
)
from modules.agents.base import AgentConfig, BaseIdeananceAgent
from modules.agents.deps import GovernanceDeps


class GovernanceControl(BaseModel):
    control_id: str
    title: str
    description: str
    framework: str
    category: str


class PolicyCitation(BaseModel):
    framework: str
    section_id: str
    section_title: str
    relevance: str


class PolicyExplanation(BaseModel):
    """Structured output from the Policy Interpreter."""

    applicable_controls: list[GovernanceControl]
    citations: list[PolicyCitation]
    plain_language_explanation: str
    implementation_guidance: str


INTERPRETER_CONFIG = AgentConfig(
    agent_id=AGENT_IDS["POLICY_INTERPRETER"],
    primary_model=MODELS["DOMAIN"],
    token_budget_in=TOKEN_BUDGETS["policy_interpreter"]["in"],
    token_budget_out=TOKEN_BUDGETS["policy_interpreter"]["out"],
    timeout_ms=TIMEOUTS_MS["policy_interpreter"],
    streaming=True,
)


class PolicyInterpreter(BaseIdeananceAgent[PolicyExplanation, GovernanceDeps]):
    def __init__(self, config: AgentConfig | None = None) -> None:
        super().__init__(config or INTERPRETER_CONFIG)

    def _create_agent(self) -> Agent[Any, Any]:
        agent: Agent[GovernanceDeps, PolicyExplanation] = Agent(
            model=self._build_model(),
            output_type=PolicyExplanation,
            deps_type=GovernanceDeps,
            output_retries=self.config.max_retries,
            instructions=(
                "You are the Policy Interpreter for Ideanance.\n\n"
                "Your job: explain governance requirements in plain "
                "language with exact citations to source frameworks. "
                "Provide hierarchical explanations and actionable "
                "implementation guidance.\n\n"
                "Rules:\n"
                "- Never hallucinate governance policies or sections.\n"
                "- Never provide legal advice.\n"
                "- Every explanation must cite exact framework section IDs.\n"
                "- Acknowledge ambiguity honestly.\n"
            ),
        )

        @agent.tool
        async def search_governance_policies(
            ctx: RunContext[GovernanceDeps], query: str
        ) -> str:
            """Search governance policies via keyword matching."""
            policies = ctx.deps.active_policies
            matches = [
                p
                for p in policies
                if query.lower() in json.dumps(p).lower()
            ]
            return json.dumps(matches[:POLICY_SEARCH_LIMIT], default=str)

        @agent.tool
        async def list_framework_sections(
            ctx: RunContext[GovernanceDeps], framework: str
        ) -> str:
            """List all sections within a governance framework."""
            sections = [
                {"id": p.get("policy_id", ""), "name": p.get("name", "")}
                for p in ctx.deps.active_policies
                if p.get("framework", "") == framework
            ]
            return json.dumps(sections, default=str)

        return agent

    def _build_fallback(self) -> PolicyExplanation:
        return PolicyExplanation(
            applicable_controls=[],
            citations=[],
            plain_language_explanation=(
                "Unable to interpret policies at this time. "
                "Please try again."
            ),
            implementation_guidance="",
        )
