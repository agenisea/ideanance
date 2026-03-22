"""Citation fidelity evaluation.

Tests that governance results only reference real
policy section IDs. Deterministic — no LLM calls.
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
EU_DIR = (
    Path(__file__).resolve().parents[2]
    / "governance-policies"
    / "eu-ai-act"
)

# Build allowlist of real section IDs
nist = load_framework_policies(NIST_DIR)
eu = load_framework_policies(EU_DIR)
VALID_IDS = {p.id for p in nist + eu}

engine = GovernanceEngine()


def run_eval() -> None:
    """Verify all policy IDs in results are real."""
    all_policies = nist + eu
    design = {"design": {"purpose": "Test agent"}}

    passed = 0
    total = 0

    for policy in all_policies:
        total += 1
        result = engine.evaluate_policy(
            artifact=design,
            policy_id=policy.id,
            framework=policy.framework,
            category=policy.category,
            severity=policy.severity,
            rules=policy.rules,
        )
        # Verify policy_id is in allowlist
        ok = result.policy_id in VALID_IDS
        if not ok:
            print(
                f"  FAIL: Unknown policy_id"
                f" '{result.policy_id}'"
            )
        else:
            passed += 1

    print(
        f"\n{passed}/{total} policy IDs validated"
        f" against allowlist"
    )
    if passed == total:
        print("  All citations reference real policies")


if __name__ == "__main__":
    run_eval()
