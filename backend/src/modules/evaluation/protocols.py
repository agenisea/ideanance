"""Protocol interfaces for evaluation repositories."""

from __future__ import annotations

from typing import Protocol

from core.constants import DEFAULT_LIST_LIMIT
from modules.evaluation.models import EvalCriterion, Evaluation


class EvaluationRepo(Protocol):
    async def create(
        self, project_id: str, **kwargs: object
    ) -> Evaluation: ...
    async def get_by_id(
        self, evaluation_id: str
    ) -> Evaluation | None: ...
    async def list_by_project(
        self, project_id: str, limit: int = DEFAULT_LIST_LIMIT
    ) -> list[Evaluation]: ...


class EvalCriterionRepo(Protocol):
    async def create(
        self, evaluation_id: str, **kwargs: object
    ) -> EvalCriterion: ...
    async def get_by_id(
        self, criterion_id: str
    ) -> EvalCriterion | None: ...
    async def list_by_evaluation(
        self, evaluation_id: str
    ) -> list[EvalCriterion]: ...
