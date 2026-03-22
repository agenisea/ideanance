"""BaseIdeananceAgent — shared agent infrastructure with FallbackModel.

Uses pydantic-ai v1.0+ API:
- output_type (not result_type)
- result.output (not result.data)
- output_retries (not result_retries)
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import structlog
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelAPIError
from pydantic_ai.models.fallback import FallbackModel

from core.resilience.protocols import (
    ResilientExecutorProtocol,
)

log = structlog.get_logger()


@dataclass
class AgentConfig:
    """Configuration for an Ideanance agent."""

    agent_id: str
    primary_model: str
    fallback_models: list[str] = field(
        default_factory=lambda: [
            "openai:gpt-4o",
            "anthropic:claude-haiku-4-5",
        ]
    )
    token_budget_in: int = 3000
    token_budget_out: int = 2000
    timeout_ms: int = 5000
    max_retries: int = 3
    streaming: bool = True
    model_override: Any | None = None  # For testing: pass TestModel()


@dataclass
class AgentRunMetadata:
    """Metadata returned alongside every agent result."""

    agent_id: str
    execution_time_ms: float
    model_used: str
    from_fallback: bool
    token_usage: dict[str, int]


class BaseIdeananceAgent[TResult: BaseModel, TDeps](ABC):
    """Base class for all Ideanance pydantic-ai agents.

    Accepts optional ResilientExecutorProtocol via constructor
    for circuit breaker + fallback chain integration.
    When no executor is provided (e.g., in tests), falls back
    to direct execution with timeout.
    """

    def __init__(
        self,
        config: AgentConfig,
        executor: ResilientExecutorProtocol | None = None,
    ) -> None:
        self.config = config
        self._executor = executor
        self._agent = self._create_agent()

    @property
    def id(self) -> str:
        return self.config.agent_id

    def _build_model(self) -> Any:
        """Build a FallbackModel from the config's model chain.

        If model_override is set (e.g., TestModel), use it directly.
        """
        if self.config.model_override is not None:
            return self.config.model_override
        if self.config.fallback_models:
            return FallbackModel(
                self.config.primary_model,
                *self.config.fallback_models,
                fallback_on=(ModelAPIError,),
            )
        return self.config.primary_model

    @abstractmethod
    def _create_agent(self) -> Agent[Any, Any]: ...

    @abstractmethod
    def _build_fallback(self) -> TResult: ...

    async def run(
        self, prompt: str, *, deps: TDeps
    ) -> tuple[TResult, AgentRunMetadata]:
        """Execute the agent with resilience, timeout, and metadata."""
        start = time.monotonic()
        timeout_s = self.config.timeout_ms / 1000

        if self._executor:
            output, from_fallback, token_usage, model = (
                await self._run_with_executor(
                    prompt, deps, timeout_s
                )
            )
        else:
            output, from_fallback, token_usage, model = (
                await self._run_direct(
                    prompt, deps, timeout_s
                )
            )

        self._log_budget(token_usage)

        elapsed_ms = (time.monotonic() - start) * 1000
        metadata = AgentRunMetadata(
            agent_id=self.config.agent_id,
            execution_time_ms=round(elapsed_ms, 1),
            model_used=model,
            from_fallback=from_fallback,
            token_usage=token_usage,
        )
        return output, metadata

    async def _run_with_executor(
        self,
        prompt: str,
        deps: Any,
        timeout_s: float,
    ) -> tuple[TResult, bool, dict[str, int], str]:
        """Execute through ResilientExecutor."""
        assert self._executor is not None
        primary = self.config.primary_model

        fallback_result = await self._executor.execute(
            lambda: asyncio.wait_for(
                self._agent.run(prompt, deps=deps),
                timeout=timeout_s,
            )
        )

        if fallback_result.level_name == "honest_error":
            return (
                self._build_fallback(),
                True,
                {"input": 0, "output": 0},
                primary,
            )

        pydantic_result = fallback_result.result
        output: TResult = pydantic_result.output
        usage = pydantic_result.usage()
        token_usage = {
            "input": usage.input_tokens or 0,
            "output": usage.output_tokens or 0,
        }
        # Extract actual model from result
        model = getattr(
            pydantic_result, "model_name", primary
        ) or primary
        return (
            output,
            fallback_result.level > 0,
            token_usage,
            model,
        )

    async def _run_direct(
        self,
        prompt: str,
        deps: Any,
        timeout_s: float,
    ) -> tuple[TResult, bool, dict[str, int], str]:
        """Direct execution with timeout."""
        primary = self.config.primary_model
        try:
            result = await asyncio.wait_for(
                self._agent.run(prompt, deps=deps),
                timeout=timeout_s,
            )
            output: TResult = result.output
            usage = result.usage()
            token_usage = {
                "input": usage.input_tokens or 0,
                "output": usage.output_tokens or 0,
            }
            model = getattr(
                result, "model_name", primary
            ) or primary
            return output, False, token_usage, model
        except Exception:
            return (
                self._build_fallback(),
                True,
                {"input": 0, "output": 0},
                primary,
            )

    def _log_budget(self, token_usage: dict[str, int]) -> None:
        """Advisory budget logging — not blocking."""
        budget_in = self.config.token_budget_in
        budget_out = self.config.token_budget_out
        actual_in = token_usage.get("input", 0)
        actual_out = token_usage.get("output", 0)

        if actual_in > budget_in:
            log.warning(
                "agent.token_budget_exceeded",
                agent_id=self.config.agent_id,
                direction="input",
                actual=actual_in,
                budget=budget_in,
            )
        if actual_out > budget_out:
            log.warning(
                "agent.token_budget_exceeded",
                agent_id=self.config.agent_id,
                direction="output",
                actual=actual_out,
                budget=budget_out,
            )

    def run_stream(
        self, prompt: str, *, deps: Any
    ):  # type: ignore[no-untyped-def]
        """Returns async context manager for streaming."""
        return self._agent.run_stream(prompt, deps=deps)
