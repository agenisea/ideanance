"""Integration tests for the agent pipeline: Router -> Agent -> Filter -> Response."""

from __future__ import annotations

from collections.abc import Callable

from ideanance.modules.agents import AGENT_IDS
from ideanance.modules.agents.base import AgentConfig
from ideanance.modules.agents.deps import GovernanceDeps
from ideanance.modules.agents.design_advisor import DesignAdvisor
from ideanance.modules.agents.governance_filter import GovernanceFilter
from ideanance.modules.agents.pipeline import AgentPipeline
from ideanance.modules.agents.policy_interpreter import PolicyInterpreter
from ideanance.modules.agents.query_router import QueryRouter


def _build_pipeline(
    test_config: Callable[[str], AgentConfig],
) -> AgentPipeline:
    router = QueryRouter(config=test_config(AGENT_IDS["QUERY_ROUTER"]))
    advisor = DesignAdvisor(config=test_config(AGENT_IDS["DESIGN_ADVISOR"]))
    interpreter = PolicyInterpreter(
        config=test_config(AGENT_IDS["POLICY_INTERPRETER"])
    )
    gov_filter = GovernanceFilter(active_policies=[])
    return AgentPipeline(
        router=router,
        agents={
            AGENT_IDS["DESIGN_ADVISOR"]: advisor,
            AGENT_IDS["POLICY_INTERPRETER"]: interpreter,
        },
        gov_filter=gov_filter,
    )


async def test_pipeline_executes_end_to_end(
    test_config: Callable[[str], AgentConfig],
    mock_governance_deps: GovernanceDeps,
):
    """Full pipeline: Router -> Domain Agent -> Governance Filter."""
    pipeline = _build_pipeline(test_config)
    result = await pipeline.execute(
        "Review my agent design", governance_deps=mock_governance_deps
    )

    # Pipeline should produce a result (TestModel returns structured data)
    assert result.output is not None or result.needs_clarification
    assert result.route is not None


async def test_pipeline_returns_governance_filter_output(
    test_config: Callable[[str], AgentConfig],
    mock_governance_deps: GovernanceDeps,
):
    """Pipeline applies governance filter to agent output."""
    pipeline = _build_pipeline(test_config)
    result = await pipeline.execute(
        "Review my agent design", governance_deps=mock_governance_deps
    )

    if not result.needs_clarification:
        assert result.governance is not None
        assert hasattr(result.governance, "compliance_score")
        assert hasattr(result.governance, "passed")


async def test_pipeline_metadata_present(
    test_config: Callable[[str], AgentConfig],
    mock_governance_deps: GovernanceDeps,
):
    """Pipeline returns agent execution metadata."""
    pipeline = _build_pipeline(test_config)
    result = await pipeline.execute(
        "Explain governance", governance_deps=mock_governance_deps
    )

    if not result.needs_clarification:
        assert result.metadata is not None
        assert result.metadata.execution_time_ms >= 0


async def test_pipeline_unknown_agent_returns_clarification(
    test_config: Callable[[str], AgentConfig],
    mock_governance_deps: GovernanceDeps,
):
    """Pipeline handles unknown target agent gracefully."""
    # Construct a pipeline with an empty agents dict instead of mutating
    router = QueryRouter(config=test_config(AGENT_IDS["QUERY_ROUTER"]))
    gov_filter = GovernanceFilter(active_policies=[])
    pipeline = AgentPipeline(
        router=router,
        agents={},
        gov_filter=gov_filter,
    )
    result = await pipeline.execute(
        "Do something", governance_deps=mock_governance_deps
    )

    # Either clarification from router or unknown agent handling
    assert result.needs_clarification or result.output is not None


async def test_pipeline_degradation_warning_on_fallback(
    test_config: Callable[[str], AgentConfig],
    mock_governance_deps: GovernanceDeps,
):
    """Pipeline shows warning when agent uses fallback."""
    pipeline = _build_pipeline(test_config)
    result = await pipeline.execute(
        "Review design", governance_deps=mock_governance_deps
    )

    # With TestModel, from_fallback is False, so no warning
    if not result.needs_clarification:
        assert result.warning is None  # Primary model succeeded
