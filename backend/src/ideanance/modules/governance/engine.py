"""Deterministic governance policy evaluation engine.

No LLM calls. Evaluates design artifacts against structured policy rules.
Budget: <100ms per evaluation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from ideanance.modules.governance.constants import (
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_WARN,
)


@dataclass
class PolicyRule:
    """A single rule within a governance policy."""

    check: str
    target: str
    message: str
    params: dict[str, Any] | None = None


@dataclass(frozen=True)
class CheckResult:
    """Result of evaluating a single rule."""

    rule: PolicyRule
    status: str  # STATUS_PASS | STATUS_WARN | STATUS_FAIL
    message: str
    details: dict[str, Any] | None = None


@dataclass(frozen=True)
class PolicyCheckResult:
    """Result of evaluating all rules in a policy."""

    policy_id: str
    framework: str
    category: str
    severity: str
    results: list[CheckResult]
    score: float
    status: str
    remediation: str


class GovernanceEngine:
    """Deterministic governance policy evaluator."""

    RULE_EVALUATORS: dict[str, Any] = {}

    @classmethod
    def register_rule(cls, check_type: str):  # type: ignore[no-untyped-def]
        """Decorator to register a rule evaluator function."""

        def decorator(func):  # type: ignore[no-untyped-def]
            cls.RULE_EVALUATORS[check_type] = func
            return func

        return decorator

    def evaluate(
        self,
        artifact: dict[str, Any],
        rules: list[PolicyRule],
    ) -> list[CheckResult]:
        """Evaluate all rules against a design artifact."""
        results = []
        for rule in rules:
            evaluator = self.RULE_EVALUATORS.get(rule.check)
            if evaluator is None:
                results.append(
                    CheckResult(
                        rule=rule,
                        status=STATUS_WARN,
                        message=f"Unknown rule type: {rule.check}",
                    )
                )
                continue
            results.append(evaluator(artifact, rule))
        return results

    def compute_score(self, results: list[CheckResult]) -> float:
        """Fraction of rules that passed (0.0 to 1.0)."""
        if not results:
            return 1.0
        passed = sum(1 for r in results if r.status == STATUS_PASS)
        return round(passed / len(results), 2)

    def worst_status(self, results: list[CheckResult]) -> str:
        """Return the worst status from results."""
        statuses = {r.status for r in results}
        if STATUS_FAIL in statuses:
            return STATUS_FAIL
        if STATUS_WARN in statuses:
            return STATUS_WARN
        return STATUS_PASS

    def evaluate_policy(
        self,
        artifact: dict[str, Any],
        policy_id: str,
        framework: str,
        category: str,
        severity: str,
        rules: list[PolicyRule],
        remediation: str = "",
    ) -> PolicyCheckResult:
        """Evaluate a full policy and return an aggregate result."""
        results = self.evaluate(artifact, rules)
        return PolicyCheckResult(
            policy_id=policy_id,
            framework=framework,
            category=category,
            severity=severity,
            results=results,
            score=self.compute_score(results),
            status=self.worst_status(results),
            remediation=remediation,
        )

    def evaluate_with_lenses(
        self,
        artifact: dict[str, Any],
        policies: list,
        lenses: list | None = None,
    ):  # type: ignore[no-untyped-def]
        """Evaluate through governance lenses.

        Returns GovernanceVerdict. Additive — existing
        evaluate() and evaluate_policy() unchanged.
        """
        from ideanance.modules.governance.lenses.accountability import (
            AccountabilityLens,
        )
        from ideanance.modules.governance.lenses.boundary import (
            BoundaryLens,
        )
        from ideanance.modules.governance.lenses.dignity import (
            DignityLens,
        )
        from ideanance.modules.governance.lenses.privacy import (
            PrivacyLens,
        )
        from ideanance.modules.governance.lenses.transparency import (
            TransparencyLens,
        )
        from ideanance.modules.governance.synthesizer import (
            GovernanceSynthesizer,
        )

        if lenses is None:
            lenses = [
                BoundaryLens(),
                TransparencyLens(),
                AccountabilityLens(),
                PrivacyLens(),
                DignityLens(),
            ]

        lens_results = [
            lens.evaluate(artifact, policies)
            for lens in lenses
        ]
        return GovernanceSynthesizer().synthesize(
            lens_results
        )


# --- Built-in rule evaluators ---


def _resolve_path(data: dict[str, Any], path: str) -> Any:
    """Resolve a dot-path like 'design.purpose' into a value."""
    current: Any = data
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
        if current is None:
            return None
    return current


@GovernanceEngine.register_rule("field_present")
def _check_field_present(artifact: dict[str, Any], rule: PolicyRule) -> CheckResult:
    """Check that a field exists and is non-empty."""
    value = _resolve_path(artifact, rule.target)
    if value is None or value == "" or value == []:
        return CheckResult(rule=rule, status=STATUS_FAIL, message=rule.message)
    return CheckResult(rule=rule, status=STATUS_PASS, message="Field present")


@GovernanceEngine.register_rule("field_min_length")
def _check_field_min_length(
    artifact: dict[str, Any], rule: PolicyRule
) -> CheckResult:
    """Check that a text field meets minimum length."""
    value = _resolve_path(artifact, rule.target)
    min_length = (rule.params or {}).get("min_length", 1)
    if value is None or len(str(value)) < min_length:
        return CheckResult(
            rule=rule,
            status=STATUS_FAIL,
            message=f"{rule.message} (minimum {min_length} chars)",
        )
    return CheckResult(
        rule=rule, status=STATUS_PASS, message="Field meets minimum length"
    )


@GovernanceEngine.register_rule("field_one_of")
def _check_field_one_of(artifact: dict[str, Any], rule: PolicyRule) -> CheckResult:
    """Check that a field's value is one of allowed options."""
    value = _resolve_path(artifact, rule.target)
    allowed = (rule.params or {}).get("values", [])
    if value not in allowed:
        return CheckResult(
            rule=rule,
            status=STATUS_FAIL,
            message=f"{rule.message} (allowed: {', '.join(str(v) for v in allowed)})",
        )
    return CheckResult(rule=rule, status=STATUS_PASS, message="Field value is valid")


@GovernanceEngine.register_rule("field_not_empty_list")
def _check_field_not_empty_list(
    artifact: dict[str, Any], rule: PolicyRule
) -> CheckResult:
    """Check that a list field has at least one item."""
    value = _resolve_path(artifact, rule.target)
    if not isinstance(value, list) or len(value) == 0:
        return CheckResult(rule=rule, status=STATUS_FAIL, message=rule.message)
    return CheckResult(rule=rule, status=STATUS_PASS, message="List is non-empty")


@GovernanceEngine.register_rule("field_matches_pattern")
def _check_field_matches_pattern(
    artifact: dict[str, Any], rule: PolicyRule
) -> CheckResult:
    """Check that a field matches a regex pattern."""
    value = _resolve_path(artifact, rule.target)
    pattern = (rule.params or {}).get("pattern", ".*")
    try:
        if value is None or not re.match(
            pattern, str(value)
        ):
            return CheckResult(
                rule=rule,
                status=STATUS_FAIL,
                message=rule.message,
            )
    except re.error:
        return CheckResult(
            rule=rule,
            status=STATUS_WARN,
            message=f"Invalid regex: {pattern}",
        )
    return CheckResult(
        rule=rule,
        status=STATUS_PASS,
        message="Field matches pattern",
    )
