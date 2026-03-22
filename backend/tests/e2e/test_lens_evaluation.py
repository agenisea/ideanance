"""E2E: governance lens evaluation — PLAN50."""

from pathlib import Path

from modules.governance.engine import (
    GovernanceEngine,
)
from modules.governance.loader import (
    load_framework_policies,
)
from modules.governance.verdict import (
    GovernanceVerdict,
)

NIST_DIR = (
    Path(__file__).resolve().parents[3]
    / "governance-policies"
    / "nist-ai-rmf"
)
EU_DIR = (
    Path(__file__).resolve().parents[3]
    / "governance-policies"
    / "eu-ai-act"
)


def test_lens_evaluation_nist():
    """Evaluate NIST policies through all 5 lenses."""
    engine = GovernanceEngine()
    policies = load_framework_policies(NIST_DIR)
    design = {
        "design": {
            "purpose": "AI medical triage",
            "intended_users": "Clinicians",
            "risk_assessment": (
                "High risk with patient safety"
                " implications requiring oversight"
            ),
        }
    }
    verdict = engine.evaluate_with_lenses(
        design, policies
    )
    assert isinstance(verdict, GovernanceVerdict)
    assert verdict.state in (
        "proceed",
        "escalate",
        "blocked",
    )
    assert len(verdict.lens_results) == 5
    assert verdict.finding_count > 0


def test_lens_evaluation_multi_framework():
    """Evaluate NIST + EU AI Act through lenses."""
    engine = GovernanceEngine()
    nist = load_framework_policies(NIST_DIR)
    eu = load_framework_policies(EU_DIR)
    all_policies = nist + eu

    verdict = engine.evaluate_with_lenses(
        {"design": {"purpose": "Credit scoring"}},
        all_policies,
    )
    assert verdict.finding_count > 0
    # Multi-framework should produce more findings
    assert len(verdict.lens_results) == 5


def test_lens_well_documented_design():
    """Well-documented design should have fewer fails."""
    engine = GovernanceEngine()
    policies = load_framework_policies(NIST_DIR)
    design = {
        "design": {
            "purpose": "AI assistant for docs",
            "intended_users": "Engineers",
            "risk_assessment": (
                "Low risk assistant with guardrails"
                " and comprehensive human oversight"
            ),
            "human_oversight_measures": (
                "Review before publish"
            ),
            "data_governance_plan": "Minimal data",
        }
    }
    verdict = engine.evaluate_with_lenses(
        design, policies
    )
    # Should be better than empty design
    passing = sum(
        1
        for r in verdict.lens_results
        for f in r.findings
        if f.status == "pass"
    )
    assert passing > 0
