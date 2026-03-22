"""Built-in NIST AI RMF governance framework plugin.

Implements PolicyRuleProvider only (ISP — PLAN7_REFACTOR R8).
GovernanceEngine is the default PolicyChecker.
"""

from __future__ import annotations

from pathlib import Path

from ideanance.modules.governance.constants import (
    FRAMEWORK_ID_NIST_AI_RMF,
    FRAMEWORK_NIST_AI_RMF,
)
from ideanance.modules.governance.engine import PolicyRule
from ideanance.modules.governance.loader import load_framework_policies

_NIST_DIR = (
    Path(__file__).resolve().parents[6]
    / "governance-policies"
    / FRAMEWORK_ID_NIST_AI_RMF
)


class NistAiRmfPlugin:
    """Built-in NIST AI RMF PolicyRuleProvider."""

    @property
    def name(self) -> str:
        return FRAMEWORK_NIST_AI_RMF

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def framework(self) -> str:
        return FRAMEWORK_NIST_AI_RMF

    def get_policy_rules(self) -> list[PolicyRule]:
        """Load all rules from NIST AI RMF YAML fixtures."""
        policies = load_framework_policies(_NIST_DIR)
        rules: list[PolicyRule] = []
        for p in policies:
            rules.extend(p.rules)
        return rules
