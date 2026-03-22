"""GovernanceChecker — single-call API for governance checks."""

from __future__ import annotations

import sys
from pathlib import Path

from ideanance_sdk.engine import (
    PolicyCheckResult,
    evaluate_policy,
)
from ideanance_sdk.loader import load_framework_policies
from ideanance_sdk.report import GovernanceReport


def check_governance(
    design: dict,
    frameworks: list[str],
    policies_dir: str = "./governance-policies",
) -> GovernanceReport:
    """Check a design against governance frameworks.

    Pure synchronous. No server, no database, no async.
    """
    policies_path = Path(policies_dir)
    all_results: list[PolicyCheckResult] = []

    for framework_id in frameworks:
        fw_dir = policies_path / framework_id
        if not fw_dir.exists():
            print(
                f"Warning: framework '{framework_id}'"
                f" not found at {fw_dir}",
                file=sys.stderr,
            )
            continue
        policies = load_framework_policies(fw_dir)
        for policy in policies:
            result = evaluate_policy(
                artifact=design,
                policy_id=policy.id,
                framework=policy.framework,
                category=policy.category,
                severity=policy.severity,
                rules=policy.rules,
            )
            all_results.append(result)

    return GovernanceReport.from_results(all_results)
