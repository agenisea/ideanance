"""Governance audit trail — records every governance decision."""

from __future__ import annotations

import structlog
from sqlalchemy import JSON, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

log = structlog.get_logger()

# Retention: 90 days default
AUDIT_RETENTION_DAYS = 90


class GovernanceAuditEntry(
    UUIDPrimaryKeyMixin, TimestampMixin, Base
):
    """Persisted audit trail for governance decisions."""

    __tablename__ = "governance_audit"

    project_id: Mapped[str] = mapped_column(
        String(36), index=True
    )
    workspace_id: Mapped[str] = mapped_column(
        String(36), index=True
    )
    action: Mapped[str] = mapped_column(String(50))
    verdict: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[float] = mapped_column(default=1.0)
    finding_count: Mapped[int] = mapped_column(
        Integer, default=0
    )
    findings_summary: Mapped[dict] = mapped_column(
        JSON, default=dict
    )
    evidence: Mapped[dict] = mapped_column(
        JSON, default=list
    )
    triggered_by: Mapped[str] = mapped_column(
        String(100), default="user"
    )
    request_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True
    )


class GovernanceAuditService:
    """Records governance decisions for audit."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def record_check(
        self,
        project_id: str,
        workspace_id: str,
        verdict: str,
        confidence: float,
        finding_count: int,
        triggered_by: str = "user",
        request_id: str | None = None,
    ) -> GovernanceAuditEntry:
        entry = GovernanceAuditEntry(
            project_id=project_id,
            workspace_id=workspace_id,
            action="check",
            verdict=verdict,
            confidence=confidence,
            finding_count=finding_count,
            triggered_by=triggered_by,
            request_id=request_id,
        )
        self.db.add(entry)
        await self.db.flush()
        log.info(
            "audit.recorded",
            project_id=project_id,
            verdict=verdict,
        )
        return entry

    async def list_by_project(
        self,
        project_id: str,
        limit: int = 50,
    ) -> list[GovernanceAuditEntry]:
        result = await self.db.execute(
            select(GovernanceAuditEntry)
            .where(
                GovernanceAuditEntry.project_id
                == project_id
            )
            .order_by(
                GovernanceAuditEntry.created_at.desc()
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_violation_count(
        self, project_id: str
    ) -> int:
        result = await self.db.execute(
            select(GovernanceAuditEntry)
            .where(
                GovernanceAuditEntry.project_id
                == project_id,
                GovernanceAuditEntry.verdict == "blocked",
            )
            .limit(1000)
        )
        return len(result.scalars().all())
