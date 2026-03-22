"""Tests for GovernanceChecker and report generation."""

from pathlib import Path

from ideanance_sdk import check_governance
from ideanance_sdk.engine import PolicyRule, evaluate, evaluate_policy
from ideanance_sdk.report import GovernanceReport

POLICIES_DIR = str(
    Path(__file__).resolve().parents[2] / "governance-policies"
)


def test_check_governance_nist():
    report = check_governance(
        design={
            "design": {
                "purpose": "Credit scoring AI",
                "intended_users": "Risk analysts",
                "risk_assessment": (
                    "Medium risk system with bias mitigation"
                    " and human oversight requirements"
                ),
            }
        },
        frameworks=["nist-ai-rmf"],
        policies_dir=POLICIES_DIR,
    )
    assert report.total_policies > 0
    assert report.overall_score >= 0
    assert report.pass_count + report.fail_count + report.warn_count == report.total_policies


def test_check_governance_eu_ai_act():
    report = check_governance(
        design={"design": {"purpose": "Chatbot"}},
        frameworks=["eu-ai-act"],
        policies_dir=POLICIES_DIR,
    )
    assert report.total_policies > 0


def test_check_governance_multi_framework():
    report = check_governance(
        design={"design": {"purpose": "AI agent"}},
        frameworks=["nist-ai-rmf", "eu-ai-act"],
        policies_dir=POLICIES_DIR,
    )
    frameworks = {r.framework for r in report.results}
    assert "NIST AI RMF" in frameworks
    assert "EU AI Act" in frameworks


def test_check_governance_unknown_framework():
    report = check_governance(
        design={"design": {}},
        frameworks=["nonexistent"],
        policies_dir=POLICIES_DIR,
    )
    assert report.total_policies == 0
    assert report.passed is True


def test_evaluate_rules():
    rules = [
        PolicyRule(
            check="field_present",
            target="design.purpose",
            message="Must have purpose",
        ),
    ]
    results = evaluate(
        {"design": {"purpose": "Test"}}, rules
    )
    assert len(results) == 1
    assert results[0].status == "pass"


def test_evaluate_rules_fail():
    rules = [
        PolicyRule(
            check="field_present",
            target="design.purpose",
            message="Must have purpose",
        ),
    ]
    results = evaluate({"design": {}}, rules)
    assert results[0].status == "fail"


def test_report_json():
    report = check_governance(
        design={"design": {"purpose": "Test"}},
        frameworks=["nist-ai-rmf"],
        policies_dir=POLICIES_DIR,
    )
    json_str = report.as_json()
    assert "overall_score" in json_str
    assert "results" in json_str


def test_report_yaml():
    report = check_governance(
        design={"design": {"purpose": "Test"}},
        frameworks=["nist-ai-rmf"],
        policies_dir=POLICIES_DIR,
    )
    yaml_str = report.as_yaml()
    assert "overall_score" in yaml_str


def test_report_markdown():
    report = check_governance(
        design={"design": {"purpose": "Test"}},
        frameworks=["nist-ai-rmf"],
        policies_dir=POLICIES_DIR,
    )
    md = report.as_markdown()
    assert "# Governance Check" in md
    assert "| Policy |" in md


def test_report_ci():
    report = check_governance(
        design={"design": {"purpose": "Test"}},
        frameworks=["nist-ai-rmf"],
        policies_dir=POLICIES_DIR,
    )
    ci = report.as_ci()
    assert "PASS" in ci or "FAIL" in ci
    assert "policies passed" in ci
