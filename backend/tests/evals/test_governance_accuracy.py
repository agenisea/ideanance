"""Governance accuracy tests using golden datasets.

Tier 1 (deterministic): Tests the governance engine against known
design inputs and expected gap/pass outcomes. No LLM required.
"""

from pathlib import Path

import pytest
import yaml

from ideanance.modules.governance.engine import GovernanceEngine
from ideanance.modules.governance.loader import load_all_policies

GOLDEN_PATH = Path(__file__).parent / "golden_datasets" / "governance_accuracy.yml"


@pytest.fixture
def engine():
    return GovernanceEngine()


@pytest.fixture
def nist_policies():
    return load_all_policies()


def _load_golden_cases():
    data = yaml.safe_load(GOLDEN_PATH.read_text())
    return data["cases"]


@pytest.mark.parametrize("case", _load_golden_cases(), ids=lambda c: c["name"])
def test_governance_accuracy_golden(case, engine, nist_policies):
    """Verify engine detects expected gaps from golden dataset."""
    design_content = case["design"]["content"]

    # Evaluate all NIST policies against design content
    results = {}
    for policy in nist_policies:
        result = engine.evaluate_policy(
            artifact=design_content,
            policy_id=policy.id,
            framework=policy.framework,
            category=policy.category,
            severity=policy.severity,
            rules=policy.rules,
        )
        results[policy.id] = {
            "status": result.status,
            "score": result.score,
        }

    # Check expected gaps
    if case.get("expected_gaps"):
        for expected_gap in case["expected_gaps"]:
            policy_id = expected_gap["policy"]
            assert policy_id in results, f"Policy {policy_id} not found in results"
            assert results[policy_id]["status"] == expected_gap["status"], (
                f"Policy {policy_id}: expected {expected_gap['status']}, "
                f"got {results[policy_id]['status']}"
            )

    # Check expected passes
    if case.get("expected_passes"):
        for expected_pass in case["expected_passes"]:
            policy_id = expected_pass["policy"]
            assert policy_id in results, f"Policy {policy_id} not found in results"
            assert results[policy_id]["status"] == expected_pass["status"], (
                f"Policy {policy_id}: expected {expected_pass['status']}, "
                f"got {results[policy_id]['status']}"
            )
