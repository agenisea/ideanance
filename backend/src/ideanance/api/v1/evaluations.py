"""Evaluation and criteria endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from ideanance.dependencies import get_evaluation_service
from ideanance.modules.evaluation.schemas import (
    EvalCriterionCreate,
    EvalCriterionRead,
    EvaluationCreate,
    EvaluationRead,
)
from ideanance.modules.evaluation.service import EvaluationService

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post(
    "/projects/{project_id}/evaluations",
    response_model=EvaluationRead,
    status_code=201,
)
async def create_evaluation(
    project_id: str,
    data: EvaluationCreate,
    svc: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationRead:
    evaluation = await svc.create_evaluation(project_id, data)
    return EvaluationRead.model_validate(evaluation)


@router.get(
    "/projects/{project_id}/evaluations",
    response_model=list[EvaluationRead],
)
async def list_evaluations(
    project_id: str,
    svc: EvaluationService = Depends(get_evaluation_service),
) -> list[EvaluationRead]:
    evaluations = await svc.list_evaluations(project_id)
    return [EvaluationRead.model_validate(e) for e in evaluations]


@router.get("/{evaluation_id}", response_model=EvaluationRead)
async def get_evaluation(
    evaluation_id: str,
    svc: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationRead:
    evaluation = await svc.get_evaluation(evaluation_id)
    if evaluation is None:
        raise HTTPException(404, "Evaluation not found")
    return EvaluationRead.model_validate(evaluation)


@router.post(
    "/{evaluation_id}/criteria",
    response_model=EvalCriterionRead,
    status_code=201,
)
async def add_criterion(
    evaluation_id: str,
    data: EvalCriterionCreate,
    svc: EvaluationService = Depends(get_evaluation_service),
) -> EvalCriterionRead:
    criterion = await svc.add_criterion(evaluation_id, data)
    return EvalCriterionRead.model_validate(criterion)


@router.get(
    "/{evaluation_id}/criteria", response_model=list[EvalCriterionRead]
)
async def list_criteria(
    evaluation_id: str,
    svc: EvaluationService = Depends(get_evaluation_service),
) -> list[EvalCriterionRead]:
    criteria = await svc.list_criteria(evaluation_id)
    return [EvalCriterionRead.model_validate(c) for c in criteria]
