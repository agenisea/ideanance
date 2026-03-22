"""Eval Generator agent — generates eval criteria from governance policies.

Uses Claude Sonnet 4.6. Every criterion MUST trace to a governance reference
(Governance-Eval Wiring pattern).
"""

from __future__ import annotations

import json
from typing import Any, Literal

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


class GovernanceCitationRef(BaseModel):
    framework: str
    section_id: str
    section_title: str = ""
    relevance: str = ""


class EvalCriterionOutput(BaseModel):
    criterion_id: str
    description: str
    metric: str
    threshold: str
    governance_reference: GovernanceCitationRef
    priority: Literal["critical", "high", "medium", "low"] = "medium"


class EvalCaseOutput(BaseModel):
    case_id: str
    criterion_id: str
    input_prompt: str
    expected_behavior: str
    case_type: Literal["positive", "negative"] = "positive"


class EvalSuite(BaseModel):
    """Structured output from the Eval Generator."""

    eval_criteria: list[EvalCriterionOutput]
    test_cases: list[EvalCaseOutput]
    governance_dimensions: list[str]
    coverage_assessment: str


EVAL_GEN_CONFIG = AgentConfig(
    agent_id=AGENT_IDS["EVAL_GENERATOR"],
    primary_model=MODELS["DOMAIN"],
    token_budget_in=TOKEN_BUDGETS["eval_generator"]["in"],
    token_budget_out=TOKEN_BUDGETS["eval_generator"]["out"],
    timeout_ms=TIMEOUTS_MS["eval_generator"],
    streaming=True,
)


class EvalGenerator(BaseIdeananceAgent[EvalSuite, GovernanceDeps]):
    def __init__(self, config: AgentConfig | None = None) -> None:
        super().__init__(config or EVAL_GEN_CONFIG)

    def _create_agent(self) -> Agent[Any, Any]:
        agent: Agent[GovernanceDeps, EvalSuite] = Agent(
            model=self._build_model(),
            output_type=EvalSuite,
            deps_type=GovernanceDeps,
            output_retries=self.config.max_retries,
            instructions=(
                "You are the Eval Generator for Ideanance.\n\n"
                "Your job: generate evaluation criteria and test cases "
                "from governance policies and agent designs. Every "
                "criterion must trace to a governance policy section "
                "(Governance-Eval Wiring pattern).\n\n"
                "Rules:\n"
                "- Every criterion must trace to a specific governance "
                "policy section.\n"
                "- Never produce vague metrics.\n"
                "- Include both positive and negative test cases.\n"
            ),
        )

        @agent.tool
        async def search_governance_policies(
            ctx: RunContext[GovernanceDeps], query: str
        ) -> str:
            """Search governance policies by keyword."""
            policies = ctx.deps.active_policies
            matches = [
                p
                for p in policies
                if query.lower() in json.dumps(p).lower()
            ]
            return json.dumps(matches[:POLICY_SEARCH_LIMIT], default=str)

        return agent

    def _build_fallback(self) -> EvalSuite:
        return EvalSuite(
            eval_criteria=[],
            test_cases=[],
            governance_dimensions=[],
            coverage_assessment=(
                "Unable to generate eval criteria at this time."
            ),
        )
