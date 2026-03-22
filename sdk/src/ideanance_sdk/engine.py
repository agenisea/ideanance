"""Deterministic governance engine — self-contained, no server deps.

Evaluates design artifacts against structured policy rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class PolicyRule:
    check: str
    target: str
    message: str
    params: dict[str, Any] | None = None


@dataclass(frozen=True)
class CheckResult:
    rule: PolicyRule
    status: str  # "pass" | "warn" | "fail"
    message: str


@dataclass(frozen=True)
class PolicyCheckResult:
    policy_id: str
    framework: str
    category: str
    severity: str
    results: list[CheckResult]
    score: float
    status: str


def _resolve_path(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
        if current is None:
            return None
    return current


RULE_EVALUATORS: dict[str, Any] = {}


def register_rule(check_type: str):  # type: ignore[no-untyped-def]
    def decorator(func):  # type: ignore[no-untyped-def]
        RULE_EVALUATORS[check_type] = func
        return func

    return decorator


@register_rule("field_present")
def _check_field_present(
    artifact: dict, rule: PolicyRule
) -> CheckResult:
    value = _resolve_path(artifact, rule.target)
    if value is None or value == "" or value == []:
        return CheckResult(
            rule=rule, status="fail", message=rule.message
        )
    return CheckResult(
        rule=rule, status="pass", message="Field present"
    )


@register_rule("field_min_length")
def _check_field_min_length(
    artifact: dict, rule: PolicyRule
) -> CheckResult:
    value = _resolve_path(artifact, rule.target)
    min_length = (rule.params or {}).get("min_length", 1)
    if value is None or len(str(value)) < min_length:
        return CheckResult(
            rule=rule,
            status="fail",
            message=f"{rule.message} (min {min_length})",
        )
    return CheckResult(
        rule=rule,
        status="pass",
        message="Field meets minimum length",
    )


@register_rule("field_one_of")
def _check_field_one_of(
    artifact: dict, rule: PolicyRule
) -> CheckResult:
    value = _resolve_path(artifact, rule.target)
    allowed = (rule.params or {}).get("values", [])
    if value not in allowed:
        return CheckResult(
            rule=rule, status="fail", message=rule.message
        )
    return CheckResult(
        rule=rule,
        status="pass",
        message="Field value is valid",
    )


@register_rule("field_not_empty_list")
def _check_field_not_empty_list(
    artifact: dict, rule: PolicyRule
) -> CheckResult:
    value = _resolve_path(artifact, rule.target)
    if not isinstance(value, list) or len(value) == 0:
        return CheckResult(
            rule=rule, status="fail", message=rule.message
        )
    return CheckResult(
        rule=rule,
        status="pass",
        message="List is non-empty",
    )


@register_rule("field_matches_pattern")
def _check_field_matches_pattern(
    artifact: dict, rule: PolicyRule
) -> CheckResult:
    value = _resolve_path(artifact, rule.target)
    pattern = (rule.params or {}).get("pattern", ".*")
    try:
        if value is None or not re.match(
            pattern, str(value)
        ):
            return CheckResult(
                rule=rule,
                status="fail",
                message=rule.message,
            )
    except re.error:
        return CheckResult(
            rule=rule,
            status="warn",
            message=f"Invalid regex: {pattern}",
        )
    return CheckResult(
        rule=rule,
        status="pass",
        message="Field matches pattern",
    )


def evaluate(
    artifact: dict[str, Any],
    rules: list[PolicyRule],
) -> list[CheckResult]:
    results = []
    for rule in rules:
        evaluator = RULE_EVALUATORS.get(rule.check)
        if evaluator is None:
            results.append(
                CheckResult(
                    rule=rule,
                    status="warn",
                    message=f"Unknown: {rule.check}",
                )
            )
            continue
        results.append(evaluator(artifact, rule))
    return results


def evaluate_policy(
    artifact: dict[str, Any],
    policy_id: str,
    framework: str,
    category: str,
    severity: str,
    rules: list[PolicyRule],
) -> PolicyCheckResult:
    results = evaluate(artifact, rules)
    passed = sum(1 for r in results if r.status == "pass")
    total = len(results) if results else 1
    worst = "pass"
    statuses = {r.status for r in results}
    if "fail" in statuses:
        worst = "fail"
    elif "warn" in statuses:
        worst = "warn"
    return PolicyCheckResult(
        policy_id=policy_id,
        framework=framework,
        category=category,
        severity=severity,
        results=results,
        score=round(passed / total, 2),
        status=worst,
    )
