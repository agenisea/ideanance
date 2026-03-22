"""Tests for multi-framework composition engine — PLAN33."""

from modules.governance.composition import (
    MultiFrameworkCompositionEngine,
)
from modules.governance.conflict_detection import ConflictDetector
from modules.governance.cross_mapping import CrossFrameworkMapper
from modules.governance.engine import GovernanceEngine, PolicyRule
from modules.governance.loader import LoadedPolicy


def _make_nist_policy() -> LoadedPolicy:
    return LoadedPolicy(
        id="nist-govern-1.1",
        framework="NIST AI RMF",
        category="govern",
        subcategory="1.1",
        name="Legal and Regulatory",
        description="Policies for AI risks",
        severity="required",
        applies_to=["agent"],
        rules=[
            PolicyRule(
                check="field_present",
                target="design.purpose",
                message="Must have purpose",
            ),
            PolicyRule(
                check="field_present",
                target="design.risk_assessment",
                message="Must have risk assessment",
            ),
        ],
        remediation={"guidance": "Add purpose and risk assessment"},
    )


def _make_eu_policy() -> LoadedPolicy:
    return LoadedPolicy(
        id="eu-art9-risk-management",
        framework="EU AI Act",
        category="high-risk",
        subcategory="Article 9",
        name="Risk Management System",
        description="Risk management system required",
        severity="required",
        applies_to=["agent"],
        rules=[
            PolicyRule(
                check="field_present",
                target="design.risk_management_plan",
                message="Must have risk management plan",
            ),
            PolicyRule(
                check="field_present",
                target="design.risk_assessment",
                message="Must have risk assessment",
            ),
        ],
        remediation={"guidance": "Establish risk management process"},
    )


def _make_engine() -> MultiFrameworkCompositionEngine:
    mapper = CrossFrameworkMapper()
    detector = ConflictDetector(mapper=mapper)
    return MultiFrameworkCompositionEngine(
        engine=GovernanceEngine(),
        conflict_detector=detector,
        mapper=mapper,
    )


def test_evaluate_single_framework():
    engine = _make_engine()
    policies = [_make_nist_policy()]
    design = {"design": {"purpose": "Credit scoring AI", "risk_assessment": "Low risk"}}

    result = engine.evaluate_all_frameworks(design, policies)
    assert result.total_policies == 1
    assert result.total_pass == 1
    assert result.composite_score == 1.0


def test_evaluate_multi_framework():
    engine = _make_engine()
    policies = [_make_nist_policy(), _make_eu_policy()]
    design = {
        "design": {
            "purpose": "Credit scoring",
            "risk_assessment": "Medium risk",
            "risk_management_plan": "Continuous monitoring process",
        }
    }

    result = engine.evaluate_all_frameworks(design, policies)
    assert result.total_policies == 2
    assert "NIST AI RMF" in result.framework_scores
    assert "EU AI Act" in result.framework_scores


def test_evaluate_failing_design():
    engine = _make_engine()
    policies = [_make_nist_policy()]
    design = {"design": {}}  # Missing all fields

    result = engine.evaluate_all_frameworks(design, policies)
    assert result.total_fail == 1
    assert result.composite_score == 0.0


def test_composite_score_severity_weighted():
    """Higher severity policies should weight more."""
    engine = _make_engine()
    required = _make_nist_policy()
    info_policy = LoadedPolicy(
        id="eu-art95-codes-of-conduct",
        framework="EU AI Act",
        category="transparency",
        subcategory="Article 95",
        name="Voluntary Codes",
        description="Voluntary",
        severity="info",
        applies_to=["agent"],
        rules=[
            PolicyRule(
                check="field_present",
                target="design.voluntary_commitments",
                message="Should have voluntary commitments",
            ),
            PolicyRule(
                check="field_present",
                target="design.ethical_guidelines",
                message="Should have ethical guidelines",
            ),
        ],
        remediation={"guidance": "Adopt codes of conduct"},
    )
    design = {
        "design": {
            "purpose": "Good",
            "risk_assessment": "Done",
            # Missing voluntary_commitments and ethical_guidelines
        }
    }
    result = engine.evaluate_all_frameworks(design, [required, info_policy])
    # Required policy passes (weight 1.0), info policy fails (weight 0.25)
    # Composite should be weighted toward the passing required policy
    assert result.composite_score > 0.5


def test_conflict_detection_finds_overlaps():
    from pathlib import Path

    cross_mappings_dir = (
        Path(__file__).resolve().parents[3]
        / "governance-policies"
        / "cross_mappings"
    )
    mapper = CrossFrameworkMapper.from_yaml_dir(cross_mappings_dir)
    detector = ConflictDetector(mapper=mapper)

    policies = [_make_nist_policy(), _make_eu_policy()]
    conflicts = detector.detect(policies)
    # Should find at least 1 conflict (both check design.risk_assessment)
    assert len(conflicts) >= 1


def test_conflict_detection_no_conflicts_single_framework():
    mapper = CrossFrameworkMapper()
    detector = ConflictDetector(mapper=mapper)
    policies = [_make_nist_policy()]  # Single framework
    conflicts = detector.detect(policies)
    assert len(conflicts) == 0


def test_framework_scores_breakdown():
    engine = _make_engine()
    policies = [_make_nist_policy(), _make_eu_policy()]
    design = {
        "design": {
            "purpose": "Credit scoring",
            "risk_assessment": "Done",
            "risk_management_plan": "Comprehensive plan",
        }
    }
    result = engine.evaluate_all_frameworks(design, policies)
    assert result.framework_scores["NIST AI RMF"] == 1.0
    assert result.framework_scores["EU AI Act"] == 1.0


def test_empty_policies():
    engine = _make_engine()
    result = engine.evaluate_all_frameworks({}, [])
    assert result.total_policies == 0
    assert result.composite_score == 1.0
    assert result.conflicts == []
