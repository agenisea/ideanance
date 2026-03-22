"""Data access layer for governance module."""

from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ideanance.modules.governance.models import (
    GovernanceCheck,
    GovernanceEvalWiring,
    GovernancePolicy,
)


class SqlGovernancePolicyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, project_id: str, **kwargs: object) -> GovernancePolicy:
        policy = GovernancePolicy(project_id=project_id, **kwargs)
        self.db.add(policy)
        await self.db.flush()
        return policy

    async def get_by_id(self, policy_id: str) -> GovernancePolicy | None:
        return await self.db.get(GovernancePolicy, policy_id)

    async def list_by_project(
        self, project_id: str, enabled_only: bool = True
    ) -> list[GovernancePolicy]:
        stmt = select(GovernancePolicy).where(
            GovernancePolicy.project_id == project_id,
            GovernancePolicy.deleted_at.is_(None),
        )
        if enabled_only:
            stmt = stmt.where(GovernancePolicy.enabled.is_(True))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_by_policy_id(
        self, project_id: str, policy_id: str
    ) -> GovernancePolicy | None:
        result = await self.db.execute(
            select(GovernancePolicy).where(
                GovernancePolicy.project_id == project_id,
                GovernancePolicy.policy_id == policy_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_enabled(
        self, policy_id: str, enabled: bool
    ) -> None:
        stmt = (
            update(GovernancePolicy)
            .where(GovernancePolicy.id == policy_id)
            .values(enabled=enabled)
        )
        await self.db.execute(stmt)
        await self.db.flush()


class SqlGovernanceEvalWiringRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, project_id: str, **kwargs: object) -> GovernanceEvalWiring:
        wiring = GovernanceEvalWiring(project_id=project_id, **kwargs)
        self.db.add(wiring)
        await self.db.flush()
        return wiring

    async def list_by_project(self, project_id: str) -> list[GovernanceEvalWiring]:
        result = await self.db.execute(
            select(GovernanceEvalWiring).where(
                GovernanceEvalWiring.project_id == project_id
            )
        )
        return list(result.scalars().all())

    async def count_by_project(self, project_id: str) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(GovernanceEvalWiring)
            .where(GovernanceEvalWiring.project_id == project_id)
        )
        return result.scalar_one()

    async def delete(self, wiring_id: str) -> bool:
        wiring = await self.db.get(GovernanceEvalWiring, wiring_id)
        if wiring is None:
            return False
        await self.db.delete(wiring)
        await self.db.flush()
        return True


class SqlGovernanceCheckRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **kwargs: object) -> GovernanceCheck:
        check = GovernanceCheck(**kwargs)
        self.db.add(check)
        await self.db.flush()
        return check
