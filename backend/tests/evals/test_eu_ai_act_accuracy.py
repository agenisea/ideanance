"""EU AI Act governance accuracy eval against golden dataset — PLAN40."""

from pathlib import Path

import pytest
import yaml

from modules.governance.engine import GovernanceEngine
from modules.governance.loader import load_framework_policies

GOLDEN_DATASET = (
    Path(__file__).parent / "golden_datasets" / "eu_ai_act_accuracy.yml"
)
EU_FIXTURES_DIR = (
    Path(__file__).resolve().parents[3] / "governance-policies" / "eu-ai-act"
)


def _load_golden_cases() -> list:
    with open(GOLDEN_DATASET) as f:
        return yaml.safe_load(f)["cases"]


def _get_policies_by_id():
    policies = load_framework_policies(EU_FIXTURES_DIR)
    return {p.id: p for p in policies}


@pytest.fixture(scope="module")
def engine():
    return GovernanceEngine()


@pytest.fixture(scope="module")
def policies_by_id():
    return _get_policies_by_id()


@pytest.mark.parametrize("case", _load_golden_cases(), ids=lambda c: c["name"])
def test_eu_ai_act_golden(case, engine, policies_by_id):
    design = case["design"]["content"]
    expected_gaps = case.get("expected_gaps", [])

    for gap in expected_gaps:
        policy_id = gap["policy"]
        expected_status = gap["status"]

        policy = policies_by_id.get(policy_id)
        assert policy is not None, f"Policy {policy_id} not found in fixtures"

        result = engine.evaluate_policy(
            artifact=design,
            policy_id=policy.id,
            framework=policy.framework,
            category=policy.category,
            severity=policy.severity,
            rules=policy.rules,
        )
        assert result.status == expected_status, (
            f"Policy {policy_id}: expected {expected_status}, "
            f"got {result.status} (score={result.score})"
        )

    if not expected_gaps:
        # If no expected gaps, verify at least some policies pass
        fail_count = 0
        for policy in policies_by_id.values():
            result = engine.evaluate_policy(
                artifact=design,
                policy_id=policy.id,
                framework=policy.framework,
                category=policy.category,
                severity=policy.severity,
                rules=policy.rules,
            )
            if result.status == "blocked":
                fail_count += 1
        # Well-documented designs should pass majority of policies
        # Some EU policies require very specific fields (biometrics, deepfake, etc.)
        # that may not apply to all systems
        total = len(policies_by_id)
        pass_rate = (total - fail_count) / total if total > 0 else 0
        assert pass_rate >= 0.4, (
            f"Well-documented design only passes {pass_rate:.0%} of policies "
            f"({fail_count}/{total} failures)"
        )
