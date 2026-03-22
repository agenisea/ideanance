"""Anti-corruption layer for governance YAML ingestion.

Shields the domain from external YAML schema changes.
If NIST/EU AI Act YAML format changes, only this file
changes — domain models remain untouched.
"""

from __future__ import annotations

from typing import Any

from ideanance.modules.governance.engine import PolicyRule
from ideanance.modules.governance.loader import (
    EvalSuggestion,
    LoadedPolicy,
)


class GovernancePolicyTranslator:
    """Maps raw YAML dict → domain LoadedPolicy.

    Single place to adapt external formats.
    """

    def translate(self, raw: dict[str, Any]) -> LoadedPolicy:
        """Translate a raw YAML policy dict to domain."""
        policy = raw.get("policy", raw)

        rules = []
        for rd in policy.get("rules", []):
            params = {
                k: v
                for k, v in rd.items()
                if k not in ("check", "target", "message")
            }
            rules.append(
                PolicyRule(
                    check=rd["check"],
                    target=rd["target"],
                    message=rd["message"],
                    params=params if params else None,
                )
            )

        eval_suggestions = [
            EvalSuggestion(
                criterion=s.get("criterion", ""),
                metric=s.get("metric", ""),
                threshold=s.get("threshold", ""),
            )
            for s in policy.get("eval_suggestions", [])
        ]

        return LoadedPolicy(
            id=policy["id"],
            framework=policy["framework"],
            category=policy["category"].lower(),
            subcategory=policy.get("subcategory", ""),
            name=policy["name"],
            description=policy.get("description", ""),
            severity=policy.get("severity", "warning"),
            applies_to=policy.get("applies_to", []),
            rules=rules,
            remediation=policy.get("remediation", {}),
            eval_suggestions=eval_suggestions,
        )


# Singleton for convenience
translator = GovernancePolicyTranslator()
