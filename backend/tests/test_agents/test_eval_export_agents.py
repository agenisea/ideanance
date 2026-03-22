"""Tests for Eval Generator and Export Formatter agents."""

from __future__ import annotations

from collections.abc import Callable

from modules.agents import AGENT_IDS
from modules.agents.base import AgentConfig
from modules.agents.deps import GovernanceDeps
from modules.agents.eval_generator import EvalGenerator, EvalSuite
from modules.agents.export_formatter import (
    ExportFormatter,
    HandoffPackage,
)

# --- Eval Generator ---


async def test_eval_generator_returns_eval_suite(
    test_config: Callable[[str], AgentConfig],
    mock_governance_deps: GovernanceDeps,
):
    gen = EvalGenerator(config=test_config(AGENT_IDS["EVAL_GENERATOR"]))
    result, metadata = await gen.run(
        "Generate eval criteria for NIST compliance",
        deps=mock_governance_deps,
    )
    assert isinstance(result, EvalSuite)
    assert metadata.agent_id == AGENT_IDS["EVAL_GENERATOR"]


def test_eval_generator_fallback(
    test_config: Callable[[str], AgentConfig],
):
    gen = EvalGenerator(config=test_config(AGENT_IDS["EVAL_GENERATOR"]))
    fallback = gen._build_fallback()
    assert len(fallback.eval_criteria) == 0
    assert "Unable to generate" in fallback.coverage_assessment


# --- Export Formatter ---


async def test_export_formatter_returns_handoff_package(
    test_config: Callable[[str], AgentConfig],
    mock_governance_deps: GovernanceDeps,
):
    fmt = ExportFormatter(
        config=test_config(AGENT_IDS["EXPORT_FORMATTER"])
    )
    result, metadata = await fmt.run(
        "Export this project as a Claude Code handoff",
        deps=mock_governance_deps,
    )
    assert isinstance(result, HandoffPackage)
    assert metadata.agent_id == AGENT_IDS["EXPORT_FORMATTER"]


def test_export_formatter_fallback(
    test_config: Callable[[str], AgentConfig],
):
    fmt = ExportFormatter(
        config=test_config(AGENT_IDS["EXPORT_FORMATTER"])
    )
    fallback = fmt._build_fallback()
    assert fallback.compliance_report.overall_score == 0.0
    assert "failed" in fallback.readme.lower()
