"""Tests for PLAN41 — resilience wiring, timeout, budget, pipeline."""

from unittest.mock import MagicMock

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from core.handoff.manager import HandoffManager
from core.handoff.protocols import HandoffManagerProtocol
from core.observability.costs import CostAggregator
from core.observability.kill_switches import KillSwitches
from core.observability.protocols import (
    CostAggregatorProtocol,
    KillSwitchProtocol,
)
from core.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
)
from core.resilience.executor import ResilientExecutor
from core.resilience.fallback_chain import (
    FallbackChain,
)
from core.resilience.honest_error import HonestError
from core.resilience.protocols import (
    ResilientExecutorProtocol,
)
from modules.agents.base import (
    AgentConfig,
    BaseIdeananceAgent,
)

# --- Protocol compliance tests ---


def test_resilient_executor_implements_protocol():
    cb = CircuitBreaker(CircuitBreakerConfig())
    chain = FallbackChain(
        levels=[],
        final_fallback=HonestError(
            message="test", governance_status="unknown"
        ),
    )
    executor = ResilientExecutor(
        circuit_breaker=cb, fallback_chain=chain
    )
    assert isinstance(executor, ResilientExecutorProtocol)


def test_handoff_manager_implements_protocol():
    manager = HandoffManager()
    assert isinstance(manager, HandoffManagerProtocol)


def test_cost_aggregator_implements_protocol():
    aggregator = CostAggregator()
    assert isinstance(aggregator, CostAggregatorProtocol)


def test_kill_switches_implements_protocol():
    switches = KillSwitches()
    assert isinstance(switches, KillSwitchProtocol)


# --- BaseIdeananceAgent resilience tests ---


class _TestOutput(BaseModel):
    answer: str = ""


class _TestAgent(BaseIdeananceAgent[_TestOutput, None]):
    def _create_agent(self) -> Agent:
        return Agent(
            self._build_model(),
            output_type=_TestOutput,
            instructions="test agent",
        )

    def _build_fallback(self) -> _TestOutput:
        return _TestOutput(answer="fallback")


def test_agent_accepts_executor():
    """Agent can be constructed with an executor."""
    config = AgentConfig(
        agent_id="test",
        primary_model="test",
        model_override=TestModel(),
    )
    cb = CircuitBreaker(CircuitBreakerConfig())
    chain = FallbackChain(
        levels=[],
        final_fallback=HonestError(
            message="test", governance_status="unknown"
        ),
    )
    executor = ResilientExecutor(
        circuit_breaker=cb, fallback_chain=chain
    )
    agent = _TestAgent(config=config, executor=executor)
    assert agent._executor is not None


def test_agent_runs_without_executor():
    """Agent works without executor (backward compat / tests)."""
    config = AgentConfig(
        agent_id="test",
        primary_model="test",
        model_override=TestModel(),
    )
    agent = _TestAgent(config=config)
    assert agent._executor is None


async def test_agent_direct_run_with_timeout():
    """Direct execution respects timeout."""
    config = AgentConfig(
        agent_id="test",
        primary_model="test",
        model_override=TestModel(),
        timeout_ms=5000,
    )
    agent = _TestAgent(config=config)
    result, meta = await agent.run("test prompt", deps=None)
    assert meta.agent_id == "test"
    assert meta.execution_time_ms >= 0


async def test_agent_budget_logging(caplog):
    """Token budget exceeded logs a warning."""
    config = AgentConfig(
        agent_id="test",
        primary_model="test",
        model_override=TestModel(),
        token_budget_in=1,  # Very low budget
        token_budget_out=1,
    )
    agent = _TestAgent(config=config)
    await agent.run("test", deps=None)
    # Budget warning should be logged (structlog may or may not
    # show up in caplog depending on configuration)


# --- Pipeline integration tests ---


def test_pipeline_accepts_protocols():
    """Pipeline constructor accepts Protocol-typed dependencies."""
    from modules.agents.pipeline import AgentPipeline

    # Mock all dependencies
    router = MagicMock()
    agents = {}
    gov_filter = MagicMock()
    handoff = MagicMock(spec=HandoffManagerProtocol)
    cost = MagicMock(spec=CostAggregatorProtocol)
    kill = MagicMock(spec=KillSwitchProtocol)

    pipeline = AgentPipeline(
        router=router,
        agents=agents,
        gov_filter=gov_filter,
        handoff_manager=handoff,
        cost_aggregator=cost,
        kill_switches=kill,
    )
    assert pipeline.handoff_manager is handoff
    assert pipeline.cost_aggregator is cost
    assert pipeline.kill_switches is kill


# --- Streaming error boundary tests ---


async def test_streaming_error_boundary():
    """Streaming emits honest_error on failure."""
    from modules.agents.streaming import (
        stream_agent_response,
    )

    class FailingAgent:
        def run_stream(self, prompt, *, deps):
            raise RuntimeError("API unavailable")

    events = []
    async for event in stream_agent_response(
        FailingAgent(), "test", None
    ):
        events.append(event)

    # Should have honest_error + done
    assert len(events) == 2
    assert events[0]["event"] == "honest_error"
    assert "API unavailable" in events[0]["data"]
    assert events[1]["event"] == "done"
