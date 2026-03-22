"""Eval suggestion engine — deterministic, no LLM calls.

Reads eval_suggestions from policy YAML data and maps them to
candidate eval criteria that can be auto-wired.
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.governance.models import GovernancePolicy


@dataclass
class EvalSuggestionResult:
    """A suggested eval criterion derived from a governance policy."""

    policy_db_id: str
    policy_id: str
    framework: str
    criterion_id: str
    description: str
    metric: str
    threshold: str
    confidence: float = 1.0
    source: str = "policy_suggestion"


class EvalSuggestionEngine:
    """Generates eval criteria suggestions from activated policies.

    Stateless — no injection needed. Pure function on policy data.
    """

    def suggest_from_policies(
        self, policies: list[GovernancePolicy]
    ) -> list[EvalSuggestionResult]:
        """Generate eval suggestions for all active policies."""
        suggestions = []
        for policy in policies:
            raw_suggestions = policy.rules.get("eval_suggestions", [])
            for idx, s in enumerate(raw_suggestions):
                suggestions.append(
                    EvalSuggestionResult(
                        policy_db_id=policy.id,
                        policy_id=policy.policy_id,
                        framework=policy.framework,
                        criterion_id=f"{policy.policy_id}-eval-{idx + 1:03d}",
                        description=s.get("criterion", ""),
                        metric=s.get("metric", ""),
                        threshold=s.get("threshold", ""),
                    )
                )
        return suggestions
