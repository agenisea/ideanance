"""Query Router agent — classifies intent and routes to domain agent.

Uses Claude Haiku 4.5 for speed. No tools, no streaming.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from modules.agents import AGENT_IDS, MODELS, TIMEOUTS_MS, TOKEN_BUDGETS
from modules.agents.base import AgentConfig, BaseIdeananceAgent
from modules.agents.deps import RouterDeps


class TaskType(StrEnum):
    GOVERNANCE_QUERY = "governance_query"
    DESIGN_REVIEW = "design_review"
    EVAL_GENERATION = "eval_generation"
    EXPORT_REQUEST = "export_request"
    CLARIFICATION = "clarification"


class RouteDecision(BaseModel):
    """Structured output from the Query Router."""

    task_type: TaskType
    target_agent: str = Field(
        description="Agent ID to route to"
    )
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(description="Brief routing rationale")


ROUTER_CONFIG = AgentConfig(
    agent_id=AGENT_IDS["QUERY_ROUTER"],
    primary_model=MODELS["ROUTING"],
    fallback_models=[],
    token_budget_in=TOKEN_BUDGETS["query_router"]["in"],
    token_budget_out=TOKEN_BUDGETS["query_router"]["out"],
    timeout_ms=TIMEOUTS_MS["query_router"],
    streaming=False,
)


class QueryRouter(BaseIdeananceAgent[RouteDecision, RouterDeps]):
    def __init__(self, config: AgentConfig | None = None) -> None:
        super().__init__(config or ROUTER_CONFIG)

    def _create_agent(self) -> Agent[Any, Any]:
        return Agent(
            model=self._build_model(),
            output_type=RouteDecision,
            deps_type=RouterDeps,
            output_retries=self.config.max_retries,
            instructions=(
                "You are the Query Router for Ideanance, a governance-first "
                "design workspace for agentic applications.\n\n"
                "Your job: classify user intent and route to one domain agent.\n\n"
                "Available agents:\n"
                "- policy_interpreter: governance frameworks, policies, compliance\n"
                "- design_advisor: agent design reviews, gap analysis, suggestions\n"
                "- eval_generator: evaluation criteria and test cases\n"
                "- export_formatter: packaging projects into handoff format\n\n"
                "Rules:\n"
                "- Never answer queries directly. Only produce routing decisions.\n"
                "- If confidence < 0.7, set task_type to 'clarification'.\n"
                "- Never hallucinate framework references.\n"
            ),
        )

    def _build_fallback(self) -> RouteDecision:
        return RouteDecision(
            task_type=TaskType.CLARIFICATION,
            target_agent="none",
            confidence=0.0,
            reasoning="Router failed — asking user to clarify intent.",
        )
