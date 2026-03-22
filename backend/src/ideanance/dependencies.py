"""Composition root: constructs repositories and injects them into services."""

from __future__ import annotations

from pathlib import Path

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ideanance.config import settings
from ideanance.core.sse import get_event_bus
from ideanance.database import get_db
from ideanance.modules.agents.topology import (
    TopologyGovernanceService,
)
from ideanance.modules.design.repository import SqlDesignRepository
from ideanance.modules.design.service import DesignService
from ideanance.modules.evaluation.repository import (
    SqlEvalCriterionRepository,
    SqlEvaluationRepository,
)
from ideanance.modules.evaluation.result_importer import (
    PromptfooResultImporter,
)
from ideanance.modules.evaluation.service import EvaluationService
from ideanance.modules.export.ci_generator import (
    CIWorkflowGenerator,
)
from ideanance.modules.export.promptfoo_exporter import (
    PromptfooExporter,
)
from ideanance.modules.export.service import ExportService
from ideanance.modules.governance.activation import (
    PolicyActivationService,
)
from ideanance.modules.governance.composition import (
    MultiFrameworkCompositionEngine,
)
from ideanance.modules.governance.conflict_detection import (
    ConflictDetector,
)
from ideanance.modules.governance.context_assembly import (
    ContextAssembler,
)
from ideanance.modules.governance.cross_mapping import (
    CrossFrameworkMapper,
)
from ideanance.modules.governance.custom_framework import (
    CustomFrameworkService,
)
from ideanance.modules.governance.engine import GovernanceEngine
from ideanance.modules.governance.repository import (
    SqlGovernanceCheckRepository,
    SqlGovernanceEvalWiringRepository,
    SqlGovernancePolicyRepository,
)
from ideanance.modules.governance.retrieval import (
    HybridRetriever,
)
from ideanance.modules.governance.service import GovernanceService
from ideanance.modules.governance.suggestions import (
    EvalSuggestionEngine,
)
from ideanance.modules.workspace.repository import (
    SqlProjectRepository,
    SqlWorkspaceRepository,
)
from ideanance.modules.workspace.service import WorkspaceService

# Shared stateless singleton (safe to reuse across requests)
_governance_engine = GovernanceEngine()

# Cross-mapping data directory
_CROSS_MAPPINGS_DIR = (
    Path(__file__).resolve().parents[2]
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
    from ideanance.core.embeddings import EmbeddingClient

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
    from ideanance.modules.templates.service import (
        TemplateService,
    )

    return TemplateService()


async def get_analytics_service(
    db: AsyncSession = Depends(get_db),
):  # type: ignore[no-untyped-def]
    from ideanance.modules.analytics.service import (
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
