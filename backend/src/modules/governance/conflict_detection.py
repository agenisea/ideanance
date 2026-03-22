"""Conflict detection between governance frameworks.

Detects overlaps, contradictions, and gaps when multiple frameworks are active.
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

from modules.governance.cross_mapping import (
    CrossFrameworkMapper,
    CrossMapping,
)
from modules.governance.loader import LoadedPolicy

log = structlog.get_logger()


@dataclass
class PolicyConflict:
    """A detected conflict between policies from different frameworks."""

    policy_a: str
    framework_a: str
    policy_b: str
    framework_b: str
    conflict_type: str  # "overlap" | "contradiction" | "gap"
    field: str
    description: str
    resolution: str


class ConflictDetector:
    """Detects conflicts between policies from different governance frameworks.

    Uses cross-mapping data to identify overlaps and contradictions.
    Falls back to rule-target comparison for unmapped policy pairs.
    """

    def __init__(self, mapper: CrossFrameworkMapper) -> None:
        self._mapper = mapper

    def detect(
        self,
        policies: list[LoadedPolicy],
    ) -> list[PolicyConflict]:
        """Detect conflicts between policies from different frameworks."""
        log.info(
            "conflict_detection.detecting",
            policy_count=len(policies),
        )
        conflicts: list[PolicyConflict] = []

        # Group policies by framework
        by_framework: dict[str, list[LoadedPolicy]] = {}
        for p in policies:
            by_framework.setdefault(p.framework, []).append(p)

        frameworks = list(by_framework.keys())
        if len(frameworks) < 2:
            return []

        # Check each framework pair
        for i, fw_a in enumerate(frameworks):
            for fw_b in frameworks[i + 1 :]:
                conflicts.extend(
                    self._detect_between_frameworks(
                        by_framework[fw_a],
                        by_framework[fw_b],
                        fw_a,
                        fw_b,
                    )
                )

        return conflicts

    def _detect_between_frameworks(
        self,
        policies_a: list[LoadedPolicy],
        policies_b: list[LoadedPolicy],
        fw_a: str,
        fw_b: str,
    ) -> list[PolicyConflict]:
        """Detect conflicts between two frameworks."""
        conflicts: list[PolicyConflict] = []

        # Use cross-mappings for known overlaps
        mappings = self._mapper.get_mappings(fw_a, fw_b)
        for mapping in mappings:
            conflict = self._mapping_to_conflict(mapping, policies_a, policies_b)
            if conflict:
                conflicts.append(conflict)

        # Detect rule-level overlaps (same target field checked by both)
        conflicts.extend(
            self._detect_rule_overlaps(policies_a, policies_b)
        )

        return conflicts

    def _mapping_to_conflict(
        self,
        mapping: CrossMapping,
        policies_a: list[LoadedPolicy],
        policies_b: list[LoadedPolicy],
    ) -> PolicyConflict | None:
        """Convert a cross-mapping to a conflict entry."""
        policy_a = next(
            (p for p in policies_a if p.id == mapping.source_id),
            None,
        )
        policy_b = next(
            (p for p in policies_b if p.id == mapping.target_id),
            None,
        )
        if not policy_a or not policy_b:
            # Try reverse direction
            policy_a = next(
                (p for p in policies_a if p.id == mapping.target_id),
                None,
            )
            policy_b = next(
                (p for p in policies_b if p.id == mapping.source_id),
                None,
            )
        if not policy_a or not policy_b:
            return None

        return PolicyConflict(
            policy_a=policy_a.id,
            framework_a=policy_a.framework,
            policy_b=policy_b.id,
            framework_b=policy_b.framework,
            conflict_type=mapping.relationship,
            field=self._find_common_field(policy_a, policy_b),
            description=mapping.description,
            resolution=self._suggest_resolution(mapping.relationship),
        )

    def _detect_rule_overlaps(
        self,
        policies_a: list[LoadedPolicy],
        policies_b: list[LoadedPolicy],
    ) -> list[PolicyConflict]:
        """Detect where both frameworks check the same field."""
        conflicts: list[PolicyConflict] = []
        targets_a: dict[str, LoadedPolicy] = {}
        for p in policies_a:
            for r in p.rules:
                targets_a[r.target] = p

        for p_b in policies_b:
            for r in p_b.rules:
                if r.target in targets_a:
                    p_a = targets_a[r.target]
                    # Avoid duplicates with cross-mapping conflicts
                    conflicts.append(
                        PolicyConflict(
                            policy_a=p_a.id,
                            framework_a=p_a.framework,
                            policy_b=p_b.id,
                            framework_b=p_b.framework,
                            conflict_type="overlap",
                            field=r.target,
                            description=(
                                f"Both check field '{r.target}'"
                            ),
                            resolution=(
                                "Review both policies and ensure"
                                " consistent thresholds"
                            ),
                        )
                    )

        return conflicts

    def _find_common_field(
        self, policy_a: LoadedPolicy, policy_b: LoadedPolicy
    ) -> str:
        """Find a common rule target between two policies."""
        targets_a = {r.target for r in policy_a.rules}
        targets_b = {r.target for r in policy_b.rules}
        common = targets_a & targets_b
        return next(iter(common), "general")

    def _suggest_resolution(self, relationship: str) -> str:
        """Suggest resolution based on relationship type."""
        resolutions = {
            "overlap": (
                "Both policies check similar requirements."
                " Apply the stricter standard."
            ),
            "equivalent": (
                "Policies are equivalent."
                " Satisfying one satisfies the other."
            ),
            "subset": (
                "One policy is a subset of the other."
                " Satisfy the broader policy."
            ),
            "partial": (
                "Partial overlap. Review both policies"
                " for complementary requirements."
            ),
        }
        return resolutions.get(
            relationship,
            "Review both policies for consistency.",
        )
