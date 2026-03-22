"""Tests for the deterministic governance engine."""

import pytest

from ideanance.modules.governance.constants import (
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_WARN,
)
from ideanance.modules.governance.engine import GovernanceEngine, PolicyRule


@pytest.fixture
def engine():
    return GovernanceEngine()


def test_field_present_pass(engine):
    rules = [
        PolicyRule(
            check="field_present", target="design.purpose", message="Need purpose"
        )
    ]
    results = engine.evaluate({"design": {"purpose": "Help users"}}, rules)
    assert results[0].status == STATUS_PASS


def test_field_present_fail_missing(engine):
    rules = [
        PolicyRule(
            check="field_present", target="design.purpose", message="Need purpose"
        )
    ]
    results = engine.evaluate({"design": {}}, rules)
    assert results[0].status == STATUS_FAIL


def test_field_present_fail_empty_string(engine):
    rules = [
        PolicyRule(
            check="field_present", target="design.purpose", message="Need purpose"
        )
    ]
    results = engine.evaluate({"design": {"purpose": ""}}, rules)
    assert results[0].status == STATUS_FAIL


def test_field_min_length_pass(engine):
    rules = [
        PolicyRule(
            check="field_min_length",
            target="design.risk",
            message="Too short",
            params={"min_length": 10},
        )
    ]
    results = engine.evaluate(
        {"design": {"risk": "This is a detailed risk assessment"}}, rules
    )
    assert results[0].status == STATUS_PASS


def test_field_min_length_fail(engine):
    rules = [
        PolicyRule(
            check="field_min_length",
            target="design.risk",
            message="Too short",
            params={"min_length": 50},
        )
    ]
    results = engine.evaluate({"design": {"risk": "Short"}}, rules)
    assert results[0].status == STATUS_FAIL


def test_field_one_of_pass(engine):
    rules = [
        PolicyRule(
            check="field_one_of",
            target="design.risk_level",
            message="Invalid",
            params={"values": ["low", "medium", "high"]},
        )
    ]
    results = engine.evaluate({"design": {"risk_level": "medium"}}, rules)
    assert results[0].status == STATUS_PASS


def test_field_one_of_fail(engine):
    rules = [
        PolicyRule(
            check="field_one_of",
            target="design.risk_level",
            message="Invalid",
            params={"values": ["low", "medium", "high"]},
        )
    ]
    results = engine.evaluate({"design": {"risk_level": "extreme"}}, rules)
    assert results[0].status == STATUS_FAIL


def test_field_not_empty_list_pass(engine):
    rules = [
        PolicyRule(
            check="field_not_empty_list", target="design.users", message="Need users"
        )
    ]
    results = engine.evaluate({"design": {"users": ["engineers"]}}, rules)
    assert results[0].status == STATUS_PASS


def test_field_not_empty_list_fail(engine):
    rules = [
        PolicyRule(
            check="field_not_empty_list", target="design.users", message="Need users"
        )
    ]
    results = engine.evaluate({"design": {"users": []}}, rules)
    assert results[0].status == STATUS_FAIL


def test_field_matches_pattern_pass(engine):
    rules = [
        PolicyRule(
            check="field_matches_pattern",
            target="design.version",
            message="Bad format",
            params={"pattern": r"^\d+\.\d+\.\d+$"},
        )
    ]
    results = engine.evaluate({"design": {"version": "1.2.3"}}, rules)
    assert results[0].status == STATUS_PASS


def test_field_matches_pattern_fail(engine):
    rules = [
        PolicyRule(
            check="field_matches_pattern",
            target="design.version",
            message="Bad format",
            params={"pattern": r"^\d+\.\d+\.\d+$"},
        )
    ]
    results = engine.evaluate({"design": {"version": "abc"}}, rules)
    assert results[0].status == STATUS_FAIL


def test_unknown_rule_type_warns(engine):
    rules = [PolicyRule(check="nonexistent_check", target="x", message="msg")]
    results = engine.evaluate({}, rules)
    assert results[0].status == STATUS_WARN
    assert "Unknown rule type" in results[0].message


def test_score_computation(engine):
    rules = [
        PolicyRule(check="field_present", target="design.a", message="m1"),
        PolicyRule(check="field_present", target="design.b", message="m2"),
        PolicyRule(check="field_present", target="design.c", message="m3"),
    ]
    results = engine.evaluate({"design": {"a": "yes", "b": "yes"}}, rules)
    score = engine.compute_score(results)
    assert score == pytest.approx(0.67, abs=0.01)


def test_worst_status(engine):
    rules = [
        PolicyRule(check="field_present", target="design.a", message="m1"),
        PolicyRule(check="field_present", target="design.missing", message="m2"),
    ]
    results = engine.evaluate({"design": {"a": "yes"}}, rules)
    assert engine.worst_status(results) == STATUS_FAIL


def test_evaluate_policy_aggregate(engine):
    rules = [
        PolicyRule(
            check="field_present", target="design.purpose", message="Need purpose"
        ),
    ]
    result = engine.evaluate_policy(
        artifact={"design": {"purpose": "Help users"}},
        policy_id="test-1",
        framework="Test",
        category="TEST",
        severity="error",
        rules=rules,
        remediation="Fix it",
    )
    assert result.status == STATUS_PASS
    assert result.score == 1.0
    assert result.policy_id == "test-1"
