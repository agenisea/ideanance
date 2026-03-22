"""Deterministic governance engine evaluation.

Tests that GovernanceEngine correctly flags violations
for known design artifacts. No LLM calls.
"""

from __future__ import annotations

from pathlib import Path

from modules.governance.engine import (
    GovernanceEngine,
)
from modules.governance.loader import (
    load_framework_policies,
)

NIST_DIR = (
    Path(__file__).resolve().parents[2]
    / "governance-policies"
    / "nist-ai-rmf"
)

engine = GovernanceEngine()
policies = load_framework_policies(NIST_DIR)
by_id = {p.id: p for p in policies}


def eval_policy(
    policy_id: str, design: dict
) -> str:
    """Evaluate a single policy and return status."""
    policy = by_id[policy_id]
    result = engine.evaluate_policy(
        artifact=design,
        policy_id=policy.id,
        framework=policy.framework,
        category=policy.category,
        severity=policy.severity,
        rules=policy.rules,
    )
    return result.status


# --- Evaluation cases ---

CASES = [
    {
        "name": "missing_purpose_fails_govern_1_1",
        "policy": "nist-govern-1.1",
        "design": {"design": {}},
        "expected": "blocked",
    },
    {
        "name": "with_purpose_passes_field_present",
        "policy": "nist-govern-1.1",
        "design": {
            "design": {
                "purpose": "Credit scoring AI",
                "intended_users": "Risk analysts",
                "risk_assessment": (
                    "Medium risk with comprehensive "
                    "monitoring and oversight"
                ),
            }
        },
        "expected": "pass",
    },
    {
        "name": "empty_design_fails_all",
        "policy": "nist-map-1.1",
        "design": {"design": {}},
        "expected": "blocked",
    },
]


def run_eval() -> None:
    """Run all evaluation cases."""
    passed = 0
    failed = 0
    for case in CASES:
        status = eval_policy(case["policy"], case["design"])
        ok = status == case["expected"]
        icon = "PASS" if ok else "FAIL"
        print(
            f"  {icon}: {case['name']}"
            f" (got={status}, expected={case['expected']})"
        )
        if ok:
            passed += 1
        else:
            failed += 1
    print(f"\n{passed}/{passed + failed} passed")


if __name__ == "__main__":
    run_eval()
