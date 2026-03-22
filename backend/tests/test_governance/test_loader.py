"""Tests for YAML policy loader."""

from pathlib import Path

from ideanance.modules.governance.constants import (
    CATEGORY_GOVERN,
    CATEGORY_MANAGE,
    CATEGORY_MAP,
    CATEGORY_MEASURE,
    FRAMEWORK_NIST_AI_RMF,
    NIST_GOVERN_1_1,
    NIST_POLICY_COUNT,
)
from ideanance.modules.governance.loader import (
    load_framework_policies,
    load_policy_file,
)

FIXTURES_DIR = (
    Path(__file__).resolve().parents[3] / "governance-policies" / "nist-ai-rmf"
)


def test_load_single_policy_file():
    path = FIXTURES_DIR / "govern" / "govern-1-1.yml"
    policy = load_policy_file(path)

    assert policy.id == NIST_GOVERN_1_1
    assert policy.framework == FRAMEWORK_NIST_AI_RMF
    assert policy.category == CATEGORY_GOVERN
    assert policy.severity == "error"
    assert len(policy.rules) == 3
    assert policy.rules[0].check == "field_present"
    assert policy.rules[0].target == "design.purpose"


def test_load_all_nist_fixtures():
    policies = load_framework_policies(FIXTURES_DIR)

    assert len(policies) == NIST_POLICY_COUNT
    frameworks = {p.framework for p in policies}
    assert frameworks == {FRAMEWORK_NIST_AI_RMF}
    categories = {p.category for p in policies}
    assert categories == {
        CATEGORY_GOVERN,
        CATEGORY_MAP,
        CATEGORY_MEASURE,
        CATEGORY_MANAGE,
    }


def test_all_policies_have_rules():
    policies = load_framework_policies(FIXTURES_DIR)
    for p in policies:
        assert len(p.rules) >= 2, f"{p.id} has fewer than 2 rules"


def test_all_policies_have_remediation():
    policies = load_framework_policies(FIXTURES_DIR)
    for p in policies:
        assert "guidance" in p.remediation, (
            f"{p.id} missing remediation guidance"
        )


def test_all_policies_have_eval_suggestions():
    policies = load_framework_policies(FIXTURES_DIR)
    for p in policies:
        assert len(p.eval_suggestions) >= 1, (
            f"{p.id} missing eval_suggestions"
        )
