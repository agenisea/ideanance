"""Shared fixtures for agent tests.

Provides reusable test_config, mock_governance_deps, and mock_router_deps
fixtures so each test file doesn't duplicate setup logic.
"""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import MagicMock

import pytest
from pydantic_ai.models.test import TestModel

from modules.agents import AGENT_IDS
from modules.agents.base import AgentConfig
from modules.agents.deps import GovernanceDeps, RouterDeps
from modules.governance.constants import (
    CATEGORY_GOVERN,
    FRAMEWORK_NIST_AI_RMF,
    NIST_GOVERN_1_1,
)


@pytest.fixture
def test_config() -> Callable[[str], AgentConfig]:
    """Factory fixture: call with an agent_id to get an AgentConfig using TestModel."""

    def _factory(agent_id: str) -> AgentConfig:
        return AgentConfig(
            agent_id=agent_id,
            primary_model="test",
            fallback_models=[],
            model_override=TestModel(),
        )

    return _factory


@pytest.fixture
def mock_governance_deps() -> GovernanceDeps:
    """Standard GovernanceDeps with NIST AI RMF, empty agent_specs."""
    return GovernanceDeps(
        workspace_id="ws-1",
        project_id="proj-1",
        active_frameworks=[FRAMEWORK_NIST_AI_RMF],
        active_policies=[
            {
                "policy_id": NIST_GOVERN_1_1,
                "framework": FRAMEWORK_NIST_AI_RMF,
                "name": "Legal Requirements",
                "category": CATEGORY_GOVERN,
            }
        ],
        agent_specs=[],
        policy_repo=MagicMock(),
        design_repo=MagicMock(),
        eval_repo=MagicMock(),
    )


@pytest.fixture
def mock_router_deps() -> RouterDeps:
    """Standard RouterDeps with all four domain agents."""
    return RouterDeps(
        workspace_id="ws-1",
        project_id="proj-1",
        available_agents=[
            AGENT_IDS["POLICY_INTERPRETER"],
            AGENT_IDS["DESIGN_ADVISOR"],
            AGENT_IDS["EVAL_GENERATOR"],
            AGENT_IDS["EXPORT_FORMATTER"],
        ],
    )
