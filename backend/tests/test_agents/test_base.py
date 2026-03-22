"""Tests for BaseIdeananceAgent infrastructure."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from ideanance.modules.agents import AGENT_IDS, MODELS, TIMEOUTS_MS, TOKEN_BUDGETS
from ideanance.modules.agents.base import (
    AgentConfig,
    AgentRunMetadata,
    BaseIdeananceAgent,
)


class MockOutput(BaseModel):
    answer: str
    score: float = 0.0


class MockAgent(BaseIdeananceAgent[MockOutput, None]):
    def _create_agent(self) -> Agent[Any, Any]:
        return Agent(
            model=TestModel(),
            output_type=MockOutput,
            instructions="You are a test agent.",
        )

    def _build_fallback(self) -> MockOutput:
        return MockOutput(answer="fallback", score=0.0)


def test_agent_constants_complete():
    assert len(AGENT_IDS) == 5
    assert "QUERY_ROUTER" in AGENT_IDS
    assert MODELS["DOMAIN"] == "anthropic:claude-sonnet-4-6"
    assert MODELS["ROUTING"] == "anthropic:claude-haiku-4-5"
    assert TIMEOUTS_MS["query_router"] == 500
    assert TOKEN_BUDGETS["design_advisor"]["in"] == 3000


def test_agent_config_defaults():
    config = AgentConfig(agent_id="test", primary_model="test:model")
    assert len(config.fallback_models) == 2
    assert config.timeout_ms == 5000
    assert config.max_retries == 3


async def test_base_agent_run_with_test_model():
    config = AgentConfig(
        agent_id="test_agent",
        primary_model="test",
        fallback_models=[],
    )
    agent = MockAgent(config)

    result, metadata = await agent.run("test prompt", deps=None)

    assert isinstance(result, MockOutput)
    assert isinstance(metadata, AgentRunMetadata)
    assert metadata.agent_id == "test_agent"
    assert metadata.execution_time_ms >= 0
    assert metadata.from_fallback is False
    assert "input" in metadata.token_usage


async def test_base_agent_fallback_on_error():
    config = AgentConfig(
        agent_id="failing_agent",
        primary_model="test",
        fallback_models=[],
    )

    class FailingAgent(BaseIdeananceAgent[MockOutput, None]):
        def _create_agent(self) -> Agent[Any, Any]:
            return Agent(
                model=TestModel(),
                output_type=MockOutput,
            )

        def _build_fallback(self) -> MockOutput:
            return MockOutput(answer="safe fallback", score=-1.0)

        async def run(
            self, prompt: str, *, deps: Any
        ) -> tuple[MockOutput, AgentRunMetadata]:
            # Simulate a total failure — all models down
            import time

            start = time.monotonic()
            output = self._build_fallback()
            elapsed_ms = (time.monotonic() - start) * 1000
            return output, AgentRunMetadata(
                agent_id=self.config.agent_id,
                execution_time_ms=round(elapsed_ms, 1),
                model_used=self.config.primary_model,
                from_fallback=True,
                token_usage={"input": 0, "output": 0},
            )

    agent = FailingAgent(config)
    result, metadata = await agent.run("test", deps=None)

    assert result.answer == "safe fallback"
    assert metadata.from_fallback is True


def test_agent_id_property():
    config = AgentConfig(agent_id="my_agent", primary_model="test")
    agent = MockAgent(config)
    assert agent.id == "my_agent"
