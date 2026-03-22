"""Integration endpoints — promptfoo, CI workflow generation."""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dependencies import (
    get_ci_generator,
    get_promptfoo_exporter,
    get_result_importer,
)
from modules.evaluation.result_importer import (
    PromptfooResultImporter,
)
from modules.export.ci_generator import (
    CIWorkflowGenerator,
)
from modules.export.promptfoo_exporter import (
    EvalCriterionInput,
    PromptfooExporter,
)

router = APIRouter(
    prefix="/integrations", tags=["integrations"]
)


class PromptfooConfigRequest(BaseModel):
    project_name: str
    criteria: list[dict[str, str]]
    provider: str = "anthropic:messages:claude-sonnet-4-6"


class PromptfooResultsUpload(BaseModel):
    results: dict[str, Any]


class CIWorkflowRequest(BaseModel):
    project_name: str
    frameworks: list[str] = []
    pass_threshold: int = 90


@router.post("/promptfoo/config")
async def export_promptfoo_config(
    request: PromptfooConfigRequest,
    exporter: PromptfooExporter = Depends(
        get_promptfoo_exporter
    ),
) -> dict[str, str]:
    criteria = [
        EvalCriterionInput(
            criterion_id=c.get("criterion_id", ""),
            description=c.get("description", ""),
            metric=c.get("metric", ""),
            threshold=c.get("threshold", ""),
            governance_wiring=c.get(
                "governance_wiring", ""
            ),
            framework=c.get("framework", ""),
        )
        for c in request.criteria
    ]
    yaml_content = exporter.export_config(
        request.project_name,
        criteria,
        request.provider,
    )
    return {"yaml": yaml_content}


@router.post("/promptfoo/results")
async def import_promptfoo_results(
    body: PromptfooResultsUpload,
    importer: PromptfooResultImporter = Depends(
        get_result_importer
    ),
) -> dict[str, Any]:
    result = importer.import_results(body.results)
    return {
        "total_tests": result.total_tests,
        "passed": result.passed,
        "failed": result.failed,
        "pass_rate": result.pass_rate,
        "threshold_breached": result.threshold_breached,
    }


@router.post("/ci-workflow")
async def generate_ci_workflow(
    request: CIWorkflowRequest,
    generator: CIWorkflowGenerator = Depends(
        get_ci_generator
    ),
) -> dict[str, str]:
    yaml_content = generator.generate(
        project_name=request.project_name,
        frameworks=request.frameworks,
        pass_threshold=request.pass_threshold,
    )
    return {"yaml": yaml_content}
