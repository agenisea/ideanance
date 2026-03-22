"""Analytics service — 3 core metrics + snapshot."""

from __future__ import annotations

from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ideanance.modules.analytics.models import (
    GovernanceSnapshot,
)
from ideanance.modules.governance.models import (
    GovernanceEvalWiring,
    GovernancePolicy,
)

log = structlog.get_logger()

# Retention: 90 days
RETENTION_DAYS = 90


class AnalyticsService:
    """Governance analytics — 3 core metrics."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_north_star(self) -> int:
        """Governance-Wired Projects count.

        Projects with at least 1 eval wiring.
        """
        result = await self.db.execute(
            select(
                func.count(
                    func.distinct(
                        GovernanceEvalWiring.project_id
                    )
                )
            )
        )
        return result.scalar_one()

    async def get_project_score(
        self, project_id: str
    ) -> float:
        """Latest snapshot score for a project."""
        result = await self.db.execute(
            select(GovernanceSnapshot)
            .where(
                GovernanceSnapshot.project_id
                == project_id
            )
            .order_by(
                GovernanceSnapshot.snapshot_date.desc()
            )
            .limit(1)
        )
        snapshot = result.scalar_one_or_none()
        return snapshot.overall_score if snapshot else 0.0

    async def get_coverage(
        self, project_id: str
    ) -> dict[str, float]:
        """Per-framework policy coverage."""
        result = await self.db.execute(
            select(GovernancePolicy).where(
                GovernancePolicy.project_id == project_id,
                GovernancePolicy.enabled.is_(True),
            )
        )
        policies = result.scalars().all()

        by_framework: dict[str, list] = {}
        for p in policies:
            by_framework.setdefault(
                p.framework, []
            ).append(p)

        coverage: dict[str, float] = {}
        for fw, fw_policies in by_framework.items():
            total = len(fw_policies)
            coverage[fw] = 1.0 if total > 0 else 0.0
        return coverage

    async def create_snapshot(
        self,
        project_id: str,
        workspace_id: str,
    ) -> GovernanceSnapshot:
        """Create a point-in-time governance snapshot."""
        # Count active policies
        pol_result = await self.db.execute(
            select(func.count())
            .select_from(GovernancePolicy)
            .where(
                GovernancePolicy.project_id == project_id,
                GovernancePolicy.enabled.is_(True),
            )
        )
        policies_active = pol_result.scalar_one()

        # Count frameworks
        fw_result = await self.db.execute(
            select(
                func.count(
                    func.distinct(
                        GovernancePolicy.framework
                    )
                )
            ).where(
                GovernancePolicy.project_id == project_id,
                GovernancePolicy.enabled.is_(True),
            )
        )
        frameworks_active = fw_result.scalar_one()

        # Count wirings
        wiring_result = await self.db.execute(
            select(func.count())
            .select_from(GovernanceEvalWiring)
            .where(
                GovernanceEvalWiring.project_id
                == project_id
            )
        )
        wirings_count = wiring_result.scalar_one()

        today = datetime.now(UTC).strftime("%Y-%m-%d")

        snapshot = GovernanceSnapshot(
            project_id=project_id,
            workspace_id=workspace_id,
            frameworks_active=frameworks_active,
            policies_active=policies_active,
            policies_passing=0,
            overall_score=(
                1.0 if wirings_count > 0 else 0.0
            ),
            wirings_count=wirings_count,
            snapshot_date=today,
        )
        self.db.add(snapshot)
        await self.db.flush()

        log.info(
            "analytics.snapshot_created",
            project_id=project_id,
            score=snapshot.overall_score,
        )
        return snapshot
