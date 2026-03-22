"""Composable security pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class SecurityCheckResult:
    passed: bool
    guard: str
    reason: str = ""
    severity: str = "info"  # "info" | "warning" | "block"


@dataclass
class SecurityPipelineResult:
    """No temporal coupling — passed is always available."""

    passed: bool
    checks: list[SecurityCheckResult] = field(
        default_factory=list
    )


class SecurityGuard(Protocol):
    """A single guard in the security pipeline."""

    def check(
        self, content: str, context: dict
    ) -> SecurityCheckResult: ...


class SecurityPipeline:
    """Composable pipeline. Runs guards in order.

    First blocking guard stops the chain.
    """

    def __init__(
        self, guards: list[SecurityGuard]
    ) -> None:
        self._guards = guards

    def run(
        self,
        content: str,
        context: dict | None = None,
    ) -> SecurityPipelineResult:
        checks: list[SecurityCheckResult] = []
        for guard in self._guards:
            result = guard.check(
                content, context or {}
            )
            checks.append(result)
            if (
                not result.passed
                and result.severity == "block"
            ):
                break
        passed = all(c.passed for c in checks)
        return SecurityPipelineResult(
            passed=passed, checks=checks
        )
