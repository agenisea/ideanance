"""Business logic for governance module."""

from __future__ import annotations

from typing import Any

from ideanance.core.events import (
    EVENT_POLICY_CREATED,
    EVENT_WIRING_CREATED,
    Event,
    EventBus,
)
from ideanance.core.observability.context import get_context
from ideanance.modules.evaluation.protocols import EvalCriterionRepo
from ideanance.modules.governance.engine import GovernanceEngine, PolicyCheckResult
from ideanance.modules.governance.models import GovernanceEvalWiring, GovernancePolicy
from ideanance.modules.governance.protocols import (
    GovernanceCheckRepo,
    GovernanceEvalWiringRepo,
    GovernancePolicyRepo,
)
from ideanance.modules.governance.schemas import (
    GovernanceEvalWiringCreate,
    GovernancePolicyCreate,
)
from ideanance.modules.governance.use_cases import RunGovernanceCheckUseCase


class GovernanceService:
    def __init__(
        self,
        policy_repo: GovernancePolicyRepo,
        wiring_repo: GovernanceEvalWiringRepo,
        check_repo: GovernanceCheckRepo,
        engine: GovernanceEngine,
        criterion_repo: EvalCriterionRepo | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.policy_repo = policy_repo
        self.wiring_repo = wiring_repo
        self.check_repo = check_repo
        self.engine = engine
        self.criterion_repo = criterion_repo
        self.event_bus = event_bus

    async def create_policy(
        self, project_id: str, data: GovernancePolicyCreate
    ) -> GovernancePolicy:
        policy = await self.policy_repo.create(
            project_id=project_id, **data.model_dump()
        )
        if self.event_bus:
            await self.event_bus.publish(
                Event(
                    type=EVENT_POLICY_CREATED,
                    workspace_id=(
                        get_context().workspace_id
                        if get_context()
                        else ""
                    ),
                    payload={
                        "project_id": project_id,
                        "policy_id": str(policy.id),
                    },
                )
            )
        return policy

    async def list_policies(
        self, project_id: str
    ) -> list[GovernancePolicy]:
        return await self.policy_repo.list_by_project(project_id)

    async def get_policy(
        self, policy_id: str
    ) -> GovernancePolicy | None:
        return await self.policy_repo.get_by_id(policy_id)

    # --- Governance-Eval Wiring (core operation) ---

    async def wire_policy_to_criterion(
        self, project_id: str, data: GovernanceEvalWiringCreate
    ) -> GovernanceEvalWiring:
        """Wire a governance policy to an eval criterion.

        Validates both policy AND criterion exist (R5: cross-context).
        Publishes domain event on success (R6).
        """
        policy = await self.policy_repo.get_by_id(data.policy_id)
        if not policy or policy.project_id != project_id:
            raise ValueError("Policy not found in project")

        if self.criterion_repo:
            criterion = await self.criterion_repo.get_by_id(
                data.criterion_id
            )
            if criterion is None:
                raise ValueError("Eval criterion not found")

        wiring = await self.wiring_repo.create(
            project_id=project_id, **data.model_dump()
        )

        if self.event_bus:
            await self.event_bus.publish(
                Event(
                    type=EVENT_WIRING_CREATED,
                    workspace_id=(
                        get_context().workspace_id
                        if get_context()
                        else ""
                    ),
                    payload={
                        "project_id": project_id,
                        "policy_id": data.policy_id,
                        "criterion_id": data.criterion_id,
                    },
                )
            )

        return wiring

    async def list_wirings(
        self, project_id: str
    ) -> list[GovernanceEvalWiring]:
        return await self.wiring_repo.list_by_project(project_id)

    async def delete_wiring(self, wiring_id: str) -> bool:
        return await self.wiring_repo.delete(wiring_id)

    async def is_project_governance_wired(
        self, project_id: str
    ) -> bool:
        return await self.wiring_repo.count_by_project(project_id) > 0

    # --- Governance Checks (delegates to use case) ---

    async def run_governance_check(
        self,
        design_content: dict[str, Any],
        project_id: str,
    ) -> list[PolicyCheckResult]:
        use_case = RunGovernanceCheckUseCase(
            policy_repo=self.policy_repo,
            engine=self.engine,
        )
        return await use_case.execute(design_content, project_id)
