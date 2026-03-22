"""Multi-framework composition engine.

Evaluates designs against multiple frameworks simultaneously,
detects conflicts, and computes composite scores.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import structlog

from modules.governance.conflict_detection import (
    ConflictDetector,
    PolicyConflict,
)
from modules.governance.constants import GovernanceState
from modules.governance.cross_mapping import CrossFrameworkMapper
from modules.governance.engine import (
    GovernanceEngine,
    PolicyCheckResult,
)
from modules.governance.loader import LoadedPolicy

log = structlog.get_logger()

# Severity weights for composite scoring
SEVERITY_WEIGHTS: dict[str, float] = {
    "required": 1.0,
    "error": 1.0,
    "warning": 0.5,
    "info": 0.25,
}


@dataclass
class CompositeResult:
    """Result of evaluating a design against multiple frameworks."""

    results: list[PolicyCheckResult]
    conflicts: list[PolicyConflict]
    composite_score: float
    framework_scores: dict[str, float]
    total_policies: int
    total_pass: int
    total_fail: int


class MultiFrameworkCompositionEngine:
    """Evaluates a design against multiple frameworks simultaneously."""

    def __init__(
        self,
        engine: GovernanceEngine,
        conflict_detector: ConflictDetector,
        mapper: CrossFrameworkMapper,
    ) -> None:
        self._engine = engine
        self._conflict_detector = conflict_detector
        self._mapper = mapper

    def evaluate_all_frameworks(
        self,
        design_content: dict[str, Any],
        policies: list[LoadedPolicy],
    ) -> CompositeResult:
        """Run all policies, detect conflicts, compute composite score."""
        log.info(
            "composition.evaluating",
            policy_count=len(policies),
        )
        # Evaluate each policy
        results: list[PolicyCheckResult] = []
        for policy in policies:
            result = self._engine.evaluate_policy(
                artifact=design_content,
                policy_id=policy.id,
                framework=policy.framework,
                category=policy.category,
                severity=policy.severity,
                rules=policy.rules,
                remediation=policy.remediation.get("guidance", ""),
            )
            results.append(result)

        # Detect conflicts
        conflicts = self._conflict_detector.detect(policies)

        # Compute scores
        composite_score = self._compute_composite_score(results)
        framework_scores = self._compute_framework_scores(results)
        total_pass = sum(1 for r in results if r.status == GovernanceState.PASS)
        total_fail = sum(1 for r in results if r.status == GovernanceState.BLOCKED)

        return CompositeResult(
            results=results,
            conflicts=conflicts,
            composite_score=composite_score,
            framework_scores=framework_scores,
            total_policies=len(policies),
            total_pass=total_pass,
            total_fail=total_fail,
        )

    def _compute_composite_score(
        self, results: list[PolicyCheckResult]
    ) -> float:
        """Weighted score across frameworks (severity-weighted)."""
        if not results:
            return 1.0

        weighted_sum = 0.0
        weight_total = 0.0
        for r in results:
            weight = SEVERITY_WEIGHTS.get(r.severity, 0.5)
            weighted_sum += r.score * weight
            weight_total += weight

        if weight_total == 0:
            return 1.0
        return round(weighted_sum / weight_total, 2)

    def _compute_framework_scores(
        self, results: list[PolicyCheckResult]
    ) -> dict[str, float]:
        """Per-framework score breakdown."""
        by_framework: dict[str, list[PolicyCheckResult]] = {}
        for r in results:
            by_framework.setdefault(r.framework, []).append(r)

        scores = {}
        for fw, fw_results in by_framework.items():
            if fw_results:
                avg = sum(r.score for r in fw_results) / len(fw_results)
                scores[fw] = round(avg, 2)
        return scores
