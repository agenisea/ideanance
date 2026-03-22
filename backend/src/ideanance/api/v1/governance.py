"""Governance endpoints: policies, wirings, checks, activation, suggestions."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ideanance.dependencies import (
    get_eval_suggestion_engine,
    get_governance_service,
    get_policy_activation_service,
)
from ideanance.modules.governance.activation import PolicyActivationService
from ideanance.modules.governance.schemas import (
    GovernanceCheckRequest,
    GovernanceCheckResponse,
    GovernanceEvalWiringCreate,
    GovernanceEvalWiringRead,
    GovernancePolicyCreate,
    GovernancePolicyRead,
)
from ideanance.modules.governance.service import GovernanceService
from ideanance.modules.governance.suggestions import EvalSuggestionEngine

router = APIRouter(prefix="/governance", tags=["governance"])


# --- Policies ---


@router.post(
    "/projects/{project_id}/policies",
    response_model=GovernancePolicyRead,
    status_code=201,
)
async def create_policy(
    project_id: str,
    data: GovernancePolicyCreate,
    svc: GovernanceService = Depends(get_governance_service),
) -> GovernancePolicyRead:
    policy = await svc.create_policy(project_id, data)
    return GovernancePolicyRead.model_validate(policy)


@router.get(
    "/projects/{project_id}/policies",
    response_model=list[GovernancePolicyRead],
)
async def list_policies(
    project_id: str,
    svc: GovernanceService = Depends(get_governance_service),
) -> list[GovernancePolicyRead]:
    policies = await svc.list_policies(project_id)
    return [GovernancePolicyRead.model_validate(p) for p in policies]


# --- Governance-Eval Wirings (THE CORE ENDPOINTS) ---


@router.post(
    "/projects/{project_id}/wirings",
    response_model=GovernanceEvalWiringRead,
    status_code=201,
)
async def create_wiring(
    project_id: str,
    data: GovernanceEvalWiringCreate,
    svc: GovernanceService = Depends(get_governance_service),
) -> GovernanceEvalWiringRead:
    try:
        wiring = await svc.wire_policy_to_criterion(project_id, data)
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    return GovernanceEvalWiringRead.model_validate(wiring)


@router.get(
    "/projects/{project_id}/wirings",
    response_model=list[GovernanceEvalWiringRead],
)
async def list_wirings(
    project_id: str,
    svc: GovernanceService = Depends(get_governance_service),
) -> list[GovernanceEvalWiringRead]:
    wirings = await svc.list_wirings(project_id)
    return [GovernanceEvalWiringRead.model_validate(w) for w in wirings]


@router.delete("/wirings/{wiring_id}", status_code=204)
async def delete_wiring(
    wiring_id: str,
    svc: GovernanceService = Depends(get_governance_service),
) -> None:
    deleted = await svc.delete_wiring(wiring_id)
    if not deleted:
        raise HTTPException(404, "Wiring not found")


# --- Governance Checks ---


@router.post("/check", response_model=GovernanceCheckResponse)
async def run_governance_check(
    request: GovernanceCheckRequest,
    svc: GovernanceService = Depends(get_governance_service),
) -> GovernanceCheckResponse:
    results = await svc.run_governance_check(
        design_content=request.design_content,
        project_id=request.project_id,
    )
    overall = (
        sum(r.score for r in results) / len(results) if results else 1.0
    )
    return GovernanceCheckResponse(
        results=[
            {
                "policy_id": r.policy_id,
                "framework": r.framework,
                "category": r.category,
                "score": r.score,
                "status": r.status,
            }
            for r in results
        ],
        overall_score=round(overall, 2),
    )


# --- Policy Activation ---


class ActivateRequest(BaseModel):
    framework_id: str


@router.post(
    "/projects/{project_id}/activate",
    response_model=list[GovernancePolicyRead],
)
async def activate_framework(
    project_id: str,
    data: ActivateRequest,
    svc: PolicyActivationService = Depends(get_policy_activation_service),
) -> list[GovernancePolicyRead]:
    try:
        policies = await svc.activate_framework(
            project_id, data.framework_id
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    return [GovernancePolicyRead.model_validate(p) for p in policies]


@router.delete(
    "/projects/{project_id}/policies/{policy_id}/deactivate",
    status_code=204,
)
async def deactivate_policy(
    project_id: str,
    policy_id: str,
    svc: PolicyActivationService = Depends(get_policy_activation_service),
) -> None:
    try:
        await svc.deactivate_policy(project_id, policy_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from None


# --- Eval Suggestions ---


@router.get(
    "/projects/{project_id}/suggestions",
    response_model=list[dict[str, Any]],
)
async def get_suggestions(
    project_id: str,
    activation_svc: PolicyActivationService = Depends(
        get_policy_activation_service
    ),
    suggestion_engine: EvalSuggestionEngine = Depends(
        get_eval_suggestion_engine
    ),
) -> list[dict[str, Any]]:
    policies = await activation_svc.get_active_policies(project_id)
    suggestions = suggestion_engine.suggest_from_policies(policies)
    return [
        {
            "policy_db_id": s.policy_db_id,
            "policy_id": s.policy_id,
            "framework": s.framework,
            "criterion_id": s.criterion_id,
            "description": s.description,
            "metric": s.metric,
            "threshold": s.threshold,
        }
        for s in suggestions
    ]


# --- Plugins ---


@router.get("/plugins", response_model=list[dict[str, str]])
async def list_plugins() -> list[dict[str, str]]:
    from ideanance.modules.governance.plugins import discover_plugins

    plugins = discover_plugins()
    return [
        {"name": p.name, "framework": p.framework, "version": p.version}
        for p in plugins.values()
    ]
