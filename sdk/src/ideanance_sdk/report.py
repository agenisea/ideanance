"""Report generation — JSON, YAML, Markdown formats."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import yaml

from ideanance_sdk.engine import PolicyCheckResult


@dataclass
class GovernanceReport:
    """Aggregated governance check report."""

    overall_score: float
    pass_count: int
    fail_count: int
    warn_count: int
    total_policies: int
    results: list[PolicyCheckResult]
    passed: bool = True

    @classmethod
    def from_results(
        cls, results: list[PolicyCheckResult]
    ) -> GovernanceReport:
        pass_count = sum(
            1 for r in results if r.status == "pass"
        )
        fail_count = sum(
            1 for r in results if r.status == "fail"
        )
        warn_count = sum(
            1 for r in results if r.status == "warn"
        )
        total = len(results) if results else 1
        score = round(pass_count / total, 2)
        return cls(
            overall_score=score,
            pass_count=pass_count,
            fail_count=fail_count,
            warn_count=warn_count,
            total_policies=len(results),
            results=results,
            passed=fail_count == 0,
        )

    def is_strict_pass(self) -> bool:
        """Strict mode: pass only if zero failures AND zero warnings."""
        return self.passed and self.warn_count == 0

    def as_json(self) -> str:
        return json.dumps(self._to_dict(), indent=2)

    def as_yaml(self) -> str:
        return yaml.dump(
            self._to_dict(),
            default_flow_style=False,
            sort_keys=False,
        )

    def as_markdown(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [
            f"# Governance Check: {status}",
            "",
            f"**Score**: {self.overall_score:.0%}",
            f"**Policies**: {self.total_policies}"
            f" ({self.pass_count} pass,"
            f" {self.fail_count} fail,"
            f" {self.warn_count} warn)",
            "",
            "| Policy | Framework | Status | Score |",
            "|--------|-----------|--------|-------|",
        ]
        for r in self.results:
            icon = (
                "PASS"
                if r.status == "pass"
                else "FAIL"
                if r.status == "fail"
                else "WARN"
            )
            lines.append(
                f"| {r.policy_id} | {r.framework}"
                f" | {icon} | {r.score:.0%} |"
            )
        return "\n".join(lines)

    def as_ci(self) -> str:
        """One-line summary for --ci flag."""
        status = "PASS" if self.passed else "FAIL"
        return (
            f"{status}: {self.pass_count}/"
            f"{self.total_policies} policies passed"
            f" (score: {self.overall_score:.0%})"
        )

    def _to_dict(self) -> dict:
        return {
            "overall_score": self.overall_score,
            "passed": self.passed,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "warn_count": self.warn_count,
            "total_policies": self.total_policies,
            "results": [
                {
                    "policy_id": r.policy_id,
                    "framework": r.framework,
                    "category": r.category,
                    "status": r.status,
                    "score": r.score,
                }
                for r in self.results
            ],
        }
