"""Policy activation service — manages which policies are active per project."""

from __future__ import annotations

from pathlib import Path

from ideanance.core.events import EVENT_FRAMEWORK_ACTIVATED, Event, EventBus
from ideanance.core.observability.context import get_context
from ideanance.modules.governance.constants import (
    FRAMEWORK_ID_EU_AI_ACT,
    FRAMEWORK_ID_NIST_AI_RMF,
)
from ideanance.modules.governance.loader import load_framework_policies
from ideanance.modules.governance.models import GovernancePolicy
from ideanance.modules.governance.protocols import GovernancePolicyRepo

_GOVERNANCE_POLICIES_DIR = (
    Path(__file__).resolve().parents[5] / "governance-policies"
)

FRAMEWORK_DIRS: dict[str, Path] = {
    FRAMEWORK_ID_NIST_AI_RMF: _GOVERNANCE_POLICIES_DIR / FRAMEWORK_ID_NIST_AI_RMF,
    FRAMEWORK_ID_EU_AI_ACT: _GOVERNANCE_POLICIES_DIR / FRAMEWORK_ID_EU_AI_ACT,
}


class PolicyActivationService:
    """Manages which policies are active for a project.

    Constructor-injected per PLAN7_REFACTOR patterns.
    """

    def __init__(
        self,
        policy_repo: GovernancePolicyRepo,
        event_bus: EventBus | None = None,
    ) -> None:
        self.policy_repo = policy_repo
        self.event_bus = event_bus

    async def activate_framework(
        self, project_id: str, framework_id: str
    ) -> list[GovernancePolicy]:
        """Activate all policies from a framework for a project."""
        framework_dir = FRAMEWORK_DIRS.get(framework_id)
        if framework_dir is None or not framework_dir.exists():
            raise ValueError(f"Unknown framework: {framework_id}")

        loaded = load_framework_policies(framework_dir)
        policies = []
        for lp in loaded:
            existing = await self.policy_repo.find_by_policy_id(
                project_id, lp.id
            )
            if existing:
                policies.append(existing)
                continue
            policy = await self.policy_repo.create(
                project_id=project_id,
                framework=lp.framework,
                policy_id=lp.id,
                name=lp.name,
                description=lp.description,
                category=lp.category,
                subcategory=lp.subcategory,
                severity=lp.severity,
                rules={
                    "rules": [
                        {
                            "check": r.check,
                            "target": r.target,
                            "message": r.message,
                            **(r.params or {}),
                        }
                        for r in lp.rules
                    ],
                    "remediation": lp.remediation,
                    "eval_suggestions": [
                        {
                            "criterion": s.criterion,
                            "metric": s.metric,
                            "threshold": s.threshold,
                        }
                        for s in lp.eval_suggestions
                    ],
                },
                enabled=True,
            )
            policies.append(policy)

        if self.event_bus:
            ctx = get_context()
            await self.event_bus.publish(
                Event(
                    type=EVENT_FRAMEWORK_ACTIVATED,
                    workspace_id=(
                        ctx.workspace_id if ctx else ""
                    ),
                    payload={
                        "project_id": project_id,
                        "framework_id": framework_id,
                        "policy_count": len(policies),
                    },
                )
            )

        return policies

    async def deactivate_policy(
        self, project_id: str, policy_db_id: str
    ) -> None:
        """Soft-disable a policy via repository update."""
        policy = await self.policy_repo.get_by_id(policy_db_id)
        if not policy or policy.project_id != project_id:
            raise ValueError("Policy not found in project")
        await self.policy_repo.update_enabled(
            policy_db_id, False
        )

    async def get_active_policies(
        self, project_id: str
    ) -> list[GovernancePolicy]:
        return await self.policy_repo.list_by_project(
            project_id, enabled_only=True
        )
