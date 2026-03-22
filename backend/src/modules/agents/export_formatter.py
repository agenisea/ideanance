"""Export Formatter agent — packages projects into Claude Code handoff format.

Uses Claude Sonnet 4.6. Every artifact carries governance provenance.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from modules.agents import AGENT_IDS, MODELS, TIMEOUTS_MS, TOKEN_BUDGETS
from modules.agents.base import AgentConfig, BaseIdeananceAgent
from modules.agents.deps import GovernanceDeps


class GovernanceCitationRef(BaseModel):
    framework: str
    section_id: str
    section_title: str = ""
    relevance: str = ""


class ExportArtifact(BaseModel):
    filename: str
    content: str
    format: str = Field(description="yaml | json | markdown")
    governance_provenance: list[GovernanceCitationRef] = Field(
        default_factory=list
    )


class ComplianceReport(BaseModel):
    overall_score: float = Field(ge=0.0, le=1.0)
    frameworks_assessed: list[str]
    gaps: list[str]
    recommendations: list[str]


class HandoffPackage(BaseModel):
    """Structured output from the Export Formatter."""

    artifacts: list[ExportArtifact]
    compliance_report: ComplianceReport
    ai_context_yml: str = Field(
        description="Content for ai-context.yml"
    )
    readme: str


EXPORT_CONFIG = AgentConfig(
    agent_id=AGENT_IDS["EXPORT_FORMATTER"],
    primary_model=MODELS["DOMAIN"],
    token_budget_in=TOKEN_BUDGETS["export_formatter"]["in"],
    token_budget_out=TOKEN_BUDGETS["export_formatter"]["out"],
    timeout_ms=TIMEOUTS_MS["export_formatter"],
    streaming=True,
)


class ExportFormatter(BaseIdeananceAgent[HandoffPackage, GovernanceDeps]):
    def __init__(self, config: AgentConfig | None = None) -> None:
        super().__init__(config or EXPORT_CONFIG)

    def _create_agent(self) -> Agent[Any, Any]:
        agent: Agent[GovernanceDeps, HandoffPackage] = Agent(
            model=self._build_model(),
            output_type=HandoffPackage,
            deps_type=GovernanceDeps,
            output_retries=self.config.max_retries,
            instructions=(
                "You are the Export Formatter for Ideanance.\n\n"
                "Your job: package project artifacts into a structured "
                "Claude Code handoff format with governance provenance "
                "on every artifact.\n\n"
                "Rules:\n"
                "- Every artifact must carry governance provenance.\n"
                "- All exports must be machine-readable.\n"
                "- Never hallucinate governance status.\n"
                "- Include ai-context.yml for Claude Code.\n"
            ),
        )

        @agent.tool
        async def get_all_agent_specs(
            ctx: RunContext[GovernanceDeps],
        ) -> str:
            """Retrieve all agent specs in the project."""
            return json.dumps(ctx.deps.agent_specs, default=str)

        @agent.tool
        async def get_governance_manifest(
            ctx: RunContext[GovernanceDeps],
        ) -> str:
            """Get governance manifest (frameworks, policies)."""
            return json.dumps(
                {
                    "frameworks": ctx.deps.active_frameworks,
                    "policy_count": len(ctx.deps.active_policies),
                },
                default=str,
            )

        return agent

    def _build_fallback(self) -> HandoffPackage:
        return HandoffPackage(
            artifacts=[],
            compliance_report=ComplianceReport(
                overall_score=0.0,
                frameworks_assessed=[],
                gaps=["Export failed — please retry"],
                recommendations=[],
            ),
            ai_context_yml="",
            readme="Export generation failed. Please retry.",
        )
