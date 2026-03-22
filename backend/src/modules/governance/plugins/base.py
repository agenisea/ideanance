"""Governance plugin protocols — split per Interface Segregation Principle."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from modules.governance.engine import CheckResult, PolicyRule


@runtime_checkable
class PolicyRuleProvider(Protocol):
    """Provides governance policy rules. Most plugins implement this only."""

    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    @property
    def framework(self) -> str: ...

    def get_policy_rules(self) -> list[PolicyRule]: ...


@runtime_checkable
class PolicyChecker(Protocol):
    """Evaluates rules against artifacts. GovernanceEngine is the default."""

    def check(
        self, artifact: dict, rules: list[PolicyRule]
    ) -> list[CheckResult]: ...
