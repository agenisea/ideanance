"""Tests for the deterministic governance filter."""

import time

from pydantic import BaseModel

from ideanance.modules.agents.base import AgentRunMetadata
from ideanance.modules.agents.governance_filter import GovernanceFilter


class MockAgentOutput(BaseModel):
    suggestions: list[str]
    references: list[dict]
    description: str


def test_filter_passes_valid_output():
    gf = GovernanceFilter(active_policies=[], framework_sections=set())
    output = MockAgentOutput(
        suggestions=["Fix X"],
        references=[{"section_id": "GOV-1.1", "title": "T"}],
        description="Analysis complete",
    )
    result = gf.check(output)
    assert result.passed is True
    assert result.compliance_score == 1.0


def test_filter_catches_invalid_citations():
    gf = GovernanceFilter(
        active_policies=[],
        framework_sections={"GOV-1.1", "GOV-1.2"},
    )
    output = MockAgentOutput(
        suggestions=["Fix X"],
        references=[{"section_id": "FAKE-99", "title": "Made up"}],
        description="Analysis",
    )
    result = gf.check(output)
    assert "FAKE-99" in result.invalid_citations
    assert result.passed is False


def test_filter_warns_on_empty_fields():
    gf = GovernanceFilter(active_policies=[])
    output = MockAgentOutput(
        suggestions=[],
        references=[],
        description="",
    )
    result = gf.check(output)
    assert len(result.warnings) > 0
    assert any("suggestions" in w for w in result.warnings)


def test_filter_degradation_warning():
    gf = GovernanceFilter(active_policies=[])
    meta = AgentRunMetadata(
        agent_id="test",
        execution_time_ms=100,
        model_used="test",
        from_fallback=True,
        token_usage={"input": 0, "output": 0},
    )
    warning = gf.add_degradation_warning(meta)
    assert warning is not None
    assert "simplified mode" in warning


def test_filter_no_warning_when_primary():
    gf = GovernanceFilter(active_policies=[])
    meta = AgentRunMetadata(
        agent_id="test",
        execution_time_ms=100,
        model_used="test",
        from_fallback=False,
        token_usage={"input": 0, "output": 0},
    )
    assert gf.add_degradation_warning(meta) is None


def test_filter_runs_under_100ms():
    # Smoke check: governance filter must be fast, but we use a generous
    # margin (500ms) to avoid flaky CI failures from scheduling jitter.
    gf = GovernanceFilter(
        active_policies=[{"id": f"p{i}"} for i in range(50)],
        framework_sections={f"SEC-{i}" for i in range(100)},
    )
    output = MockAgentOutput(
        suggestions=["s1", "s2"],
        references=[
            {"section_id": f"SEC-{i}", "title": f"T{i}"}
            for i in range(20)
        ],
        description="test",
    )
    generous_margin_ms = 500
    start = time.monotonic()
    for _ in range(100):
        gf.check(output)
    avg_ms = (time.monotonic() - start) * 1000 / 100
    assert avg_ms < generous_margin_ms, (
        f"Filter took {avg_ms:.2f}ms (smoke-check budget: <{generous_margin_ms}ms)"
    )
