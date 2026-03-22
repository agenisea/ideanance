"""Design endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_design_service
from modules.design.schemas import DesignCreate, DesignRead
from modules.design.service import DesignService

router = APIRouter(prefix="/designs", tags=["designs"])


@router.post(
    "/projects/{project_id}/designs",
    response_model=DesignRead,
    status_code=201,
)
async def create_design(
    project_id: str,
    data: DesignCreate,
    svc: DesignService = Depends(get_design_service),
) -> DesignRead:
    design = await svc.create_design(project_id, data)
    return DesignRead.model_validate(design)


@router.get(
    "/projects/{project_id}/designs", response_model=list[DesignRead]
)
async def list_designs(
    project_id: str,
    svc: DesignService = Depends(get_design_service),
) -> list[DesignRead]:
    designs = await svc.list_designs(project_id)
    return [DesignRead.model_validate(d) for d in designs]


@router.get("/{design_id}", response_model=DesignRead)
async def get_design(
    design_id: str,
    svc: DesignService = Depends(get_design_service),
) -> DesignRead:
    design = await svc.get_design(design_id)
    if design is None:
        raise HTTPException(404, "Design not found")
    return DesignRead.model_validate(design)
