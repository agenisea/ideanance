"""GovernanceSnapshot model — greenfield, no migration."""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class GovernanceSnapshot(
    UUIDPrimaryKeyMixin, TimestampMixin, Base
):
    """Point-in-time governance metrics for a project."""

    __tablename__ = "governance_snapshots"

    project_id: Mapped[str] = mapped_column(
        String(36), index=True
    )
    workspace_id: Mapped[str] = mapped_column(
        String(36), index=True
    )
    frameworks_active: Mapped[int] = mapped_column(
        Integer, default=0
    )
    policies_active: Mapped[int] = mapped_column(
        Integer, default=0
    )
    policies_passing: Mapped[int] = mapped_column(
        Integer, default=0
    )
    overall_score: Mapped[float] = mapped_column(
        default=0.0
    )
    wirings_count: Mapped[int] = mapped_column(
        Integer, default=0
    )
    snapshot_date: Mapped[str] = mapped_column(
        String(10), index=True
    )
