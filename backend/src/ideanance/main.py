"""FastAPI application entry point."""

import warnings
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ideanance.api import api_v1_router
from ideanance.api.v1.agents import router as agents_router
from ideanance.api.v1.analytics import (
    router as analytics_router,
)
from ideanance.api.v1.designs import (
    router as designs_router,
)
from ideanance.api.v1.evaluations import (
    router as evaluations_router,
)
from ideanance.api.v1.events import router as events_router
from ideanance.api.v1.exports import (
    router as exports_router,
)
from ideanance.api.v1.frameworks import (
    router as frameworks_router,
)
from ideanance.api.v1.governance import (
    router as governance_router,
)
from ideanance.api.v1.health import router as health_router
from ideanance.api.v1.integrations import (
    router as integrations_router,
)
from ideanance.api.v1.templates import (
    router as templates_router,
)
from ideanance.api.v1.topology import (
    router as topology_router,
)
from ideanance.api.v1.workspaces import (
    router as workspaces_router,
)
from ideanance.config import settings

# Wire all v1 routers into versioned parent
api_v1_router.include_router(agents_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(designs_router)
api_v1_router.include_router(evaluations_router)
api_v1_router.include_router(events_router)
api_v1_router.include_router(exports_router)
api_v1_router.include_router(frameworks_router)
api_v1_router.include_router(governance_router)
api_v1_router.include_router(integrations_router)
api_v1_router.include_router(templates_router)
api_v1_router.include_router(topology_router)
api_v1_router.include_router(workspaces_router)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Application lifespan: startup and shutdown."""
    from ideanance.database import engine
    from ideanance.models import Base, import_all_models

    import_all_models()

    from ideanance.core.logging import configure_logging
    from ideanance.core.observability import (
        configure_observability,
    )

    configure_logging(debug=settings.debug)
    configure_observability(app)

    # Production warnings
    if settings.is_production and not settings.enable_auth:
        warnings.warn(
            "AUTH DISABLED IN PRODUCTION.",
            stacklevel=2,
        )
    if settings.secret_key == "change-me-in-production":
        warnings.warn(
            "Using default SECRET_KEY.",
            stacklevel=2,
        )

    # Observability singletons on app.state
    from ideanance.core.observability.costs import (
        CostAggregator,
    )
    from ideanance.core.observability.kill_switches import (
        KillSwitches,
    )
    from ideanance.core.rate_limit import RateLimiter

    app.state.kill_switches = KillSwitches()
    app.state.cost_aggregator = CostAggregator()
    app.state.rate_limiter = RateLimiter(
        max_requests=settings.rate_limit_max_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )

    # Kill switch from env var
    if not settings.agents_enabled:
        app.state.kill_switches.disable_all_agents(
            "Disabled via AGENTS_ENABLED env var"
        )

    if settings.is_sqlite:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield

    from ideanance.database import engine as eng

    await eng.dispose()


app = FastAPI(
    title="Ideanance API",
    description=(
        "Governance-first design workspace"
        " for agentic applications"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Versioned API + health at root
app.include_router(api_v1_router)
app.include_router(health_router)
