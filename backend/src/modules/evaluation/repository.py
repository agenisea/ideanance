"""Data access layer for evaluation module."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import DEFAULT_LIST_LIMIT
from modules.evaluation.models import EvalCriterion, Evaluation


class SqlEvaluationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, project_id: str, **kwargs: object) -> Evaluation:
        evaluation = Evaluation(project_id=project_id, **kwargs)
        self.db.add(evaluation)
        await self.db.flush()
        return evaluation

    async def get_by_id(self, evaluation_id: str) -> Evaluation | None:
        return await self.db.get(Evaluation, evaluation_id)

    async def list_by_project(
        self, project_id: str, limit: int = DEFAULT_LIST_LIMIT
    ) -> list[Evaluation]:
        result = await self.db.execute(
            select(Evaluation)
            .where(Evaluation.project_id == project_id)
            .where(Evaluation.deleted_at.is_(None))
            .limit(limit)
        )
        return list(result.scalars().all())


class SqlEvalCriterionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, evaluation_id: str, **kwargs: object) -> EvalCriterion:
        criterion = EvalCriterion(evaluation_id=evaluation_id, **kwargs)
        self.db.add(criterion)
        await self.db.flush()
        return criterion

    async def get_by_id(self, criterion_id: str) -> EvalCriterion | None:
        return await self.db.get(EvalCriterion, criterion_id)

    async def list_by_evaluation(
        self, evaluation_id: str
    ) -> list[EvalCriterion]:
        result = await self.db.execute(
            select(EvalCriterion).where(
                EvalCriterion.evaluation_id == evaluation_id
            )
        )
        return list(result.scalars().all())
