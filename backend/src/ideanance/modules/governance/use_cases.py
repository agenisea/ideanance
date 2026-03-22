"""Governance use cases — extracted from GovernanceService for SRP."""

from __future__ import annotations

from typing import Any

from ideanance.modules.governance.engine import (
    GovernanceEngine,
    PolicyCheckResult,
    PolicyRule,
)
from ideanance.modules.governance.protocols import GovernancePolicyRepo


class RunGovernanceCheckUseCase:
    """Evaluate a design artifact against all active governance policies."""

    def __init__(
        self,
        policy_repo: GovernancePolicyRepo,
        engine: GovernanceEngine,
    ) -> None:
        self.policy_repo = policy_repo
        self.engine = engine

    async def execute(
        self,
        design_content: dict[str, Any],
        project_id: str,
    ) -> list[PolicyCheckResult]:
        policies = await self.policy_repo.list_by_project(project_id)
        results = []
        for policy in policies:
            rules = self._parse_rules(policy.rules)
            result = self.engine.evaluate_policy(
                artifact=design_content,
                policy_id=policy.policy_id,
                framework=policy.framework,
                category=policy.category,
                severity=policy.severity,
                rules=rules,
                remediation=policy.rules.get("remediation", {}).get(
                    "guidance", ""
                ),
            )
            results.append(result)
        return results

    def _parse_rules(self, rules_data: dict[str, Any]) -> list[PolicyRule]:
        raw_rules = rules_data.get("rules", [])
        return [
            PolicyRule(
                check=r["check"],
                target=r["target"],
                message=r["message"],
                params={
                    k: v
                    for k, v in r.items()
                    if k not in ("check", "target", "message")
                }
                or None,
            )
            for r in raw_rules
        ]
