"""Import promptfoo evaluation results back into Ideanance.

Bidirectional integration: promptfoo results → Ideanance governance dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import structlog

log = structlog.get_logger()

# Default pass rate threshold (90%)
DEFAULT_PASS_THRESHOLD = 0.90


@dataclass
class CriterionResult:
    """Result for a single criterion from promptfoo."""

    criterion_id: str
    passed: bool
    score: float = 0.0
    details: str = ""
    governance_wiring: str = ""


@dataclass
class EvalRunResult:
    """Aggregated result of an imported eval run."""

    total_tests: int
    passed: int
    failed: int
    pass_rate: float
    criterion_results: list[CriterionResult]
    threshold_breached: bool = False
    source: str = "promptfoo"


class PromptfooResultImporter:
    """Import promptfoo evaluation results.

    Stateless — parses results, no DB dependency.
    """

    def __init__(
        self,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
    ) -> None:
        self._pass_threshold = pass_threshold

    def import_results(
        self, results_json: dict[str, Any]
    ) -> EvalRunResult:
        """Parse promptfoo results and compute aggregate metrics."""
        log.info(
            "result_importer.importing",
            result_count=len(results_json.get("results", [])),
        )
        results_list = results_json.get("results", [])
        criterion_results: list[CriterionResult] = []

        for result in results_list:
            criterion_id = (
                result.get("metadata", {}).get(
                    "ideanance_criterion_id", ""
                )
                or result.get("testCase", {})
                .get("metadata", {})
                .get("ideanance_criterion_id", "")
            )
            governance_wiring = (
                result.get("metadata", {}).get("governance_wiring", "")
                or result.get("testCase", {})
                .get("metadata", {})
                .get("governance_wiring", "")
            )

            passed = result.get("success", False)
            score = result.get("score", 1.0 if passed else 0.0)

            criterion_results.append(
                CriterionResult(
                    criterion_id=criterion_id,
                    passed=passed,
                    score=score,
                    details=result.get("error", ""),
                    governance_wiring=governance_wiring,
                )
            )

        total = len(criterion_results)
        passed_count = sum(1 for r in criterion_results if r.passed)
        pass_rate = passed_count / total if total > 0 else 0.0
        threshold_breached = pass_rate < self._pass_threshold

        return EvalRunResult(
            total_tests=total,
            passed=passed_count,
            failed=total - passed_count,
            pass_rate=round(pass_rate, 4),
            criterion_results=criterion_results,
            threshold_breached=threshold_breached,
        )
