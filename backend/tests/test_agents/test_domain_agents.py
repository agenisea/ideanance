"""Tests for domain agents: Query Router, Design Advisor, Policy Interpreter.

All tests use TestModel via model_override — zero real LLM API calls.
ALLOW_MODEL_REQUESTS = False is set in conftest.py.
"""

from __future__ import annotations

from collections.abc import Callable

from modules.agents import AGENT_IDS
from modules.agents.base import AgentConfig
from modules.agents.deps import GovernanceDeps, RouterDeps
from modules.agents.design_advisor import DesignAdvice, DesignAdvisor
from modules.agents.policy_interpreter import (
    PolicyExplanation,
    PolicyInterpreter,
)
from modules.agents.query_router import QueryRouter, RouteDecision

# --- Query Router ---


async def test_query_router_returns_route_decision(
    test_config: Callable[[str], AgentConfig],
    mock_router_deps: RouterDeps,
):
    router = QueryRouter(
        config=test_config(AGENT_IDS["QUERY_ROUTER"])
    )
    result, metadata = await router.run(
        "What does NIST GOVERN-1.1 require?",
        deps=mock_router_deps,
    )
    assert isinstance(result, RouteDecision)
    assert metadata.agent_id == AGENT_IDS["QUERY_ROUTER"]


def test_query_router_fallback(
    test_config: Callable[[str], AgentConfig],
):
    router = QueryRouter(
        config=test_config(AGENT_IDS["QUERY_ROUTER"])
    )
    fallback = router._build_fallback()
    assert fallback.task_type == "clarification"
    assert fallback.confidence == 0.0


# --- Design Advisor ---


async def test_design_advisor_returns_design_advice(
    test_config: Callable[[str], AgentConfig],
    mock_governance_deps: GovernanceDeps,
):
    advisor = DesignAdvisor(
        config=test_config(AGENT_IDS["DESIGN_ADVISOR"])
    )
    result, metadata = await advisor.run(
        "Review my agent design for NIST compliance",
        deps=mock_governance_deps,
    )
    assert isinstance(result, DesignAdvice)
    assert metadata.agent_id == AGENT_IDS["DESIGN_ADVISOR"]


def test_design_advisor_fallback(
    test_config: Callable[[str], AgentConfig],
):
    advisor = DesignAdvisor(
        config=test_config(AGENT_IDS["DESIGN_ADVISOR"])
    )
    fallback = advisor._build_fallback()
    assert fallback.governance_score == 0.0
    assert len(fallback.suggestions) == 1


# --- Policy Interpreter ---


async def test_policy_interpreter_returns_explanation(
    test_config: Callable[[str], AgentConfig],
    mock_governance_deps: GovernanceDeps,
):
    interpreter = PolicyInterpreter(
        config=test_config(AGENT_IDS["POLICY_INTERPRETER"])
    )
    result, metadata = await interpreter.run(
        "Explain NIST AI RMF GOVERN-1.1",
        deps=mock_governance_deps,
    )
    assert isinstance(result, PolicyExplanation)
    assert metadata.agent_id == AGENT_IDS["POLICY_INTERPRETER"]


def test_policy_interpreter_fallback(
    test_config: Callable[[str], AgentConfig],
):
    interpreter = PolicyInterpreter(
        config=test_config(AGENT_IDS["POLICY_INTERPRETER"])
    )
    fallback = interpreter._build_fallback()
    assert "Unable to interpret" in fallback.plain_language_explanation
