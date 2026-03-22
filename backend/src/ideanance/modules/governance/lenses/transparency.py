"""TransparencyLens — documentation, disclosure, interpretability."""

from __future__ import annotations

from typing import Any

from ideanance.modules.governance.engine import GovernanceEngine
from ideanance.modules.governance.evidence import Evidence
from ideanance.modules.governance.lenses.base import (
    get_lens_names_for_policy,
)
from ideanance.modules.governance.loader import LoadedPolicy
from ideanance.modules.governance.verdict import (
    LensFinding,
    LensResult,
)

_engine = GovernanceEngine()


class TransparencyLens:
    """Evaluates documentation, disclosure, interpretability."""

    @property
    def name(self) -> str:
        return "transparency"

    def evaluate(
        self,
        artifact: dict[str, Any],
        policies: list[LoadedPolicy],
    ) -> LensResult:
        findings: list[LensFinding] = []
        for policy in policies:
            if self.name not in get_lens_names_for_policy(
                policy
            ):
                continue
            results = _engine.evaluate(
                artifact, policy.rules
            )
            for cr in results:
                findings.append(
                    LensFinding(
                        lens=self.name,
                        status=cr.status,
                        policy_id=policy.id,
                        message=cr.message,
                        evidence=[
                            Evidence(
                                claim=cr.message,
                                source="policy",
                                pointer=policy.id,
                            )
                        ],
                        confidence=1.0,
                    )
                )
        return LensResult(
            lens=self.name, findings=findings
        )
