"""Business logic for evaluation module."""

from __future__ import annotations

from ideanance.modules.evaluation.models import EvalCriterion, Evaluation
from ideanance.modules.evaluation.protocols import (
    EvalCriterionRepo,
    EvaluationRepo,
)
from ideanance.modules.evaluation.schemas import (
    EvalCriterionCreate,
    EvaluationCreate,
)


class EvaluationService:
    def __init__(
        self,
        eval_repo: EvaluationRepo,
        criterion_repo: EvalCriterionRepo,
    ) -> None:
        self.eval_repo = eval_repo
        self.criterion_repo = criterion_repo

    async def create_evaluation(
        self, project_id: str, data: EvaluationCreate
    ) -> Evaluation:
        return await self.eval_repo.create(
            project_id=project_id, **data.model_dump()
        )

    async def get_evaluation(self, evaluation_id: str) -> Evaluation | None:
        return await self.eval_repo.get_by_id(evaluation_id)

    async def list_evaluations(self, project_id: str) -> list[Evaluation]:
        return await self.eval_repo.list_by_project(project_id)

    async def add_criterion(
        self, evaluation_id: str, data: EvalCriterionCreate
    ) -> EvalCriterion:
        return await self.criterion_repo.create(
            evaluation_id=evaluation_id, **data.model_dump()
        )

    async def list_criteria(
        self, evaluation_id: str
    ) -> list[EvalCriterion]:
        return await self.criterion_repo.list_by_evaluation(evaluation_id)
