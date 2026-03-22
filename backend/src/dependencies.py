"""Composition root: constructs repositories and injects them into services."""

from __future__ import annotations

from pathlib import Path

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from core.sse import get_event_bus
from database import get_db
from modules.agents.topology import (
    TopologyGovernanceService,
)
from modules.design.repository import SqlDesignRepository
from modules.design.service import DesignService
from modules.evaluation.repository import (
    SqlEvalCriterionRepository,
    SqlEvaluationRepository,
)
from modules.evaluation.result_importer import (
    PromptfooResultImporter,
)
from modules.evaluation.service import EvaluationService
from modules.export.ci_generator import (
    CIWorkflowGenerator,
)
from modules.export.promptfoo_exporter import (
    PromptfooExporter,
)
from modules.export.service import ExportService
from modules.governance.activation import (
    PolicyActivationService,
)
from modules.governance.composition import (
    MultiFrameworkCompositionEngine,
)
from modules.governance.conflict_detection import (
    ConflictDetector,
)
from modules.governance.context_assembly import (
    ContextAssembler,
)
from modules.governance.cross_mapping import (
    CrossFrameworkMapper,
)
from modules.governance.custom_framework import (
    CustomFrameworkService,
)
from modules.governance.engine import GovernanceEngine
from modules.governance.repository import (
    SqlGovernanceCheckRepository,
    SqlGovernanceEvalWiringRepository,
    SqlGovernancePolicyRepository,
)
from modules.governance.retrieval import (
    HybridRetriever,
)
from modules.governance.service import GovernanceService
from modules.governance.suggestions import (
    EvalSuggestionEngine,
)
from modules.workspace.repository import (
    SqlProjectRepository,
    SqlWorkspaceRepository,
)
from modules.workspace.service import WorkspaceService

# Shared stateless singleton (safe to reuse across requests)
_governance_engine = GovernanceEngine()

# Cross-mapping data directory
_CROSS_MAPPINGS_DIR = (
    Path(__file__).resolve().parents[1]
    / "governance-policies"
    / "cross_mappings"
)


# --- Phase 1 factories ---


async def get_workspace_service(
    db: AsyncSession = Depends(get_db),
) -> WorkspaceService:
    return WorkspaceService(
        workspace_repo=SqlWorkspaceRepository(db),
        project_repo=SqlProjectRepository(db),
    )


async def get_governance_service(
    db: AsyncSession = Depends(get_db),
) -> GovernanceService:
    return GovernanceService(
        policy_repo=SqlGovernancePolicyRepository(db),
        wiring_repo=SqlGovernanceEvalWiringRepository(db),
        check_repo=SqlGovernanceCheckRepository(db),
        engine=_governance_engine,
        criterion_repo=SqlEvalCriterionRepository(db),
        event_bus=get_event_bus(),
    )


async def get_design_service(
    db: AsyncSession = Depends(get_db),
) -> DesignService:
    return DesignService(repo=SqlDesignRepository(db))


async def get_evaluation_service(
    db: AsyncSession = Depends(get_db),
) -> EvaluationService:
    return EvaluationService(
        eval_repo=SqlEvaluationRepository(db),
        criterion_repo=SqlEvalCriterionRepository(db),
    )


async def get_policy_activation_service(
    db: AsyncSession = Depends(get_db),
) -> PolicyActivationService:
    return PolicyActivationService(
        policy_repo=SqlGovernancePolicyRepository(db),
        event_bus=get_event_bus(),
    )


def get_eval_suggestion_engine() -> EvalSuggestionEngine:
    return EvalSuggestionEngine()


async def get_export_service(
    db: AsyncSession = Depends(get_db),
) -> ExportService:
    return ExportService(
        project_repo=SqlProjectRepository(db),
        design_repo=SqlDesignRepository(db),
        policy_repo=SqlGovernancePolicyRepository(db),
        wiring_repo=SqlGovernanceEvalWiringRepository(db),
        eval_repo=SqlEvaluationRepository(db),
        criterion_repo=SqlEvalCriterionRepository(db),
    )


# --- Phase 2 factories ---


def get_composition_engine() -> MultiFrameworkCompositionEngine:
    """Pure computation — no DB dependency."""
    mapper = CrossFrameworkMapper.from_yaml_dir(
        _CROSS_MAPPINGS_DIR
    )
    detector = ConflictDetector(mapper=mapper)
    return MultiFrameworkCompositionEngine(
        engine=_governance_engine,
        conflict_detector=detector,
        mapper=mapper,
    )


async def get_hybrid_retriever(
    db: AsyncSession = Depends(get_db),
) -> HybridRetriever:
    from core.embeddings import EmbeddingClient

    embedding_client = EmbeddingClient(
        api_key=settings.openai_api_key
    )
    return HybridRetriever(
        db=db,
        embedding_client=embedding_client,
        is_sqlite=settings.is_sqlite,
    )


async def get_context_assembler(
    db: AsyncSession = Depends(get_db),
) -> ContextAssembler:
    return ContextAssembler(db=db)


def get_topology_governance_service() -> (
    TopologyGovernanceService
):
    return TopologyGovernanceService(
        engine=_governance_engine
    )


def get_promptfoo_exporter() -> PromptfooExporter:
    return PromptfooExporter()


def get_result_importer() -> PromptfooResultImporter:
    return PromptfooResultImporter()


def get_ci_generator() -> CIWorkflowGenerator:
    return CIWorkflowGenerator()


def get_custom_framework_service() -> CustomFrameworkService:
    """In-memory for now — PLAN42 DB migration pending."""
    return CustomFrameworkService(event_bus=get_event_bus())


def get_template_service():  # type: ignore[no-untyped-def]
    """Template export/import service."""
    from modules.templates.service import (
        TemplateService,
    )

    return TemplateService()


async def get_analytics_service(
    db: AsyncSession = Depends(get_db),
):  # type: ignore[no-untyped-def]
    from modules.analytics.service import (
        AnalyticsService,
    )

    return AnalyticsService(db)


# --- Observability factories (from app.state) ---


def get_kill_switches(request: Request):  # type: ignore[no-untyped-def]
    """Kill switches from app.state (set in lifespan)."""
    return getattr(request.app.state, "kill_switches", None)


def get_cost_aggregator(request: Request):  # type: ignore[no-untyped-def]
    """Cost aggregator from app.state (set in lifespan)."""
    return getattr(
        request.app.state, "cost_aggregator", None
    )


def get_rate_limiter(request: Request):  # type: ignore[no-untyped-def]
    """Rate limiter from app.state (set in lifespan)."""
    return getattr(request.app.state, "rate_limiter", None)
