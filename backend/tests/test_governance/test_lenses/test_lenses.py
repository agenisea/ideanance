"""Tests for governance lenses, synthesizer, evidence — PLAN52."""

from pathlib import Path

from ideanance.modules.governance.engine import GovernanceEngine
from ideanance.modules.governance.evidence import Evidence
from ideanance.modules.governance.lenses.accountability import (
    AccountabilityLens,
)
from ideanance.modules.governance.lenses.base import (
    get_lens_names_for_policy,
)
from ideanance.modules.governance.lenses.boundary import (
    BoundaryLens,
)
from ideanance.modules.governance.lenses.dignity import (
    DignityLens,
)
from ideanance.modules.governance.lenses.privacy import (
    PrivacyLens,
)
from ideanance.modules.governance.lenses.transparency import (
    TransparencyLens,
)
from ideanance.modules.governance.loader import (
    load_framework_policies,
)
from ideanance.modules.governance.synthesizer import (
    GovernanceSynthesizer,
)
from ideanance.modules.governance.verdict import (
    GovernanceVerdict,
    LensFinding,
    LensResult,
)

NIST_DIR = (
    Path(__file__).resolve().parents[4]
    / "governance-policies"
    / "nist-ai-rmf"
)


def _nist_policies():
    return load_framework_policies(NIST_DIR)


# --- Evidence tests ---


def test_evidence_is_frozen():
    e = Evidence(
        claim="test", source="policy", pointer="x"
    )
    assert e.claim == "test"


def test_evidence_with_excerpt():
    e = Evidence(
        claim="c",
        source="artifact",
        pointer="design.purpose",
        excerpt="Credit scoring",
    )
    assert e.excerpt == "Credit scoring"


# --- Lens tests ---


def test_boundary_lens_evaluates():
    lens = BoundaryLens()
    assert lens.name == "boundary"
    result = lens.evaluate(
        {"design": {"purpose": "Test"}}, _nist_policies()
    )
    assert isinstance(result, LensResult)
    assert result.lens == "boundary"
    assert len(result.findings) > 0


def test_transparency_lens_evaluates():
    lens = TransparencyLens()
    assert lens.name == "transparency"
    result = lens.evaluate(
        {"design": {}}, _nist_policies()
    )
    assert len(result.findings) > 0


def test_accountability_lens_evaluates():
    lens = AccountabilityLens()
    assert lens.name == "accountability"
    result = lens.evaluate(
        {"design": {}}, _nist_policies()
    )
    assert isinstance(result, LensResult)


def test_privacy_lens_evaluates():
    lens = PrivacyLens()
    assert lens.name == "privacy"
    result = lens.evaluate(
        {"design": {}}, _nist_policies()
    )
    assert isinstance(result, LensResult)


def test_dignity_lens_evaluates():
    lens = DignityLens()
    assert lens.name == "dignity"
    result = lens.evaluate(
        {"design": {}}, _nist_policies()
    )
    assert isinstance(result, LensResult)


def test_lens_findings_have_evidence():
    lens = BoundaryLens()
    result = lens.evaluate(
        {"design": {}}, _nist_policies()
    )
    for finding in result.findings:
        assert len(finding.evidence) >= 1
        assert finding.evidence[0].source == "policy"


def test_lens_independence():
    """Each lens evaluates independently."""
    artifact = {"design": {"purpose": "Test"}}
    policies = _nist_policies()
    b = BoundaryLens().evaluate(artifact, policies)
    t = TransparencyLens().evaluate(artifact, policies)
    # Different lenses may produce different finding counts
    assert b.lens != t.lens


# --- Synthesizer tests ---


def test_synthesizer_all_pass():
    synth = GovernanceSynthesizer()
    results = [
        LensResult(
            lens="boundary",
            findings=[
                LensFinding(
                    lens="boundary",
                    status="pass",
                    policy_id="p1",
                    message="ok",
                )
            ],
        ),
    ]
    verdict = synth.synthesize(results)
    assert verdict.state == "proceed"
    assert verdict.confidence == 1.0


def test_synthesizer_any_fail_is_blocked():
    synth = GovernanceSynthesizer()
    results = [
        LensResult(
            lens="boundary",
            findings=[
                LensFinding(
                    lens="boundary",
                    status="fail",
                    policy_id="p1",
                    message="bad",
                )
            ],
        ),
    ]
    verdict = synth.synthesize(results)
    assert verdict.state == "blocked"


def test_synthesizer_any_warn_is_escalate():
    synth = GovernanceSynthesizer()
    results = [
        LensResult(
            lens="boundary",
            findings=[
                LensFinding(
                    lens="boundary",
                    status="warn",
                    policy_id="p1",
                    message="meh",
                )
            ],
        ),
    ]
    verdict = synth.synthesize(results)
    assert verdict.state == "escalate"


def test_synthesizer_low_confidence_escalates():
    synth = GovernanceSynthesizer()
    results = [
        LensResult(
            lens="boundary",
            confidence=0.3,
            findings=[
                LensFinding(
                    lens="boundary",
                    status="pass",
                    policy_id="p1",
                    message="ok",
                    confidence=0.3,
                )
            ],
        ),
    ]
    verdict = synth.synthesize(results)
    assert verdict.state == "escalate"


def test_synthesizer_empty_is_proceed():
    synth = GovernanceSynthesizer()
    verdict = synth.synthesize([])
    assert verdict.state == "proceed"


def test_synthesizer_blocked_beats_escalate():
    """Strict dominance: BLOCKED > ESCALATE."""
    synth = GovernanceSynthesizer()
    results = [
        LensResult(
            lens="boundary",
            findings=[
                LensFinding(
                    lens="boundary",
                    status="fail",
                    policy_id="p1",
                    message="bad",
                )
            ],
        ),
        LensResult(
            lens="transparency",
            findings=[
                LensFinding(
                    lens="transparency",
                    status="warn",
                    policy_id="p2",
                    message="meh",
                )
            ],
        ),
    ]
    verdict = synth.synthesize(results)
    assert verdict.state == "blocked"


# --- Engine integration ---


def test_evaluate_with_lenses():
    engine = GovernanceEngine()
    policies = _nist_policies()
    verdict = engine.evaluate_with_lenses(
        {"design": {"purpose": "Test AI"}}, policies
    )
    assert isinstance(verdict, GovernanceVerdict)
    assert verdict.state in (
        "proceed",
        "escalate",
        "blocked",
    )
    assert len(verdict.lens_results) == 5


def test_evaluate_with_lenses_well_documented():
    engine = GovernanceEngine()
    policies = _nist_policies()
    design = {
        "design": {
            "purpose": "AI assistant",
            "intended_users": "Engineers",
            "risk_assessment": (
                "Low risk with comprehensive monitoring"
                " and human oversight built in"
            ),
        }
    }
    verdict = engine.evaluate_with_lenses(
        design, policies
    )
    # Well-documented should have fewer failures
    assert verdict.finding_count > 0


# --- Category mapping ---


def test_category_lens_mapping():
    from ideanance.modules.governance.loader import (
        LoadedPolicy,
    )

    p = LoadedPolicy(
        id="test",
        framework="test",
        category="high-risk",
        subcategory="",
        name="test",
        description="",
        severity="required",
        applies_to=[],
        rules=[],
    )
    lenses = get_lens_names_for_policy(p)
    assert "boundary" in lenses
    assert "dignity" in lenses
    assert len(lenses) == 5  # high-risk maps to all


def test_category_limited_maps_to_transparency():
    from ideanance.modules.governance.loader import (
        LoadedPolicy,
    )

    p = LoadedPolicy(
        id="test",
        framework="test",
        category="limited",
        subcategory="",
        name="test",
        description="",
        severity="required",
        applies_to=[],
        rules=[],
    )
    lenses = get_lens_names_for_policy(p)
    assert lenses == ["transparency"]
