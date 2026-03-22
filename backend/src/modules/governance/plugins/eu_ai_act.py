"""Built-in EU AI Act governance framework plugin.

Implements PolicyRuleProvider only (ISP — PLAN7_REFACTOR R8).
GovernanceEngine is the default PolicyChecker.
"""

from __future__ import annotations

from pathlib import Path

from modules.governance.constants import (
    FRAMEWORK_EU_AI_ACT,
    FRAMEWORK_ID_EU_AI_ACT,
)
from modules.governance.engine import PolicyRule
from modules.governance.loader import load_framework_policies

_EU_DIR = (
    Path(__file__).resolve().parents[5]
    / "governance-policies"
    / FRAMEWORK_ID_EU_AI_ACT
)


class EuAiActPlugin:
    """Built-in EU AI Act PolicyRuleProvider."""

    @property
    def name(self) -> str:
        return FRAMEWORK_EU_AI_ACT

    @property
    def version(self) -> str:
        return "2024/1689"

    @property
    def framework(self) -> str:
        return FRAMEWORK_EU_AI_ACT

    def get_policy_rules(self) -> list[PolicyRule]:
        """Load all rules from EU AI Act YAML fixtures."""
        policies = load_framework_policies(_EU_DIR)
        rules: list[PolicyRule] = []
        for p in policies:
            rules.extend(p.rules)
        return rules
