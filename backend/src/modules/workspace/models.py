"""Workspace and Project models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from modules.design.models import Design
    from modules.evaluation.models import Evaluation
    from modules.governance.models import GovernancePolicy


class Workspace(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    settings: Mapped[dict] = mapped_column(JSON, default=dict)

    projects: Mapped[list[Project]] = relationship(
        back_populates="workspace", lazy="raise"
    )


class Project(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "projects"

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    settings: Mapped[dict] = mapped_column(JSON, default=dict)

    workspace: Mapped[Workspace] = relationship(back_populates="projects")
    governance_policies: Mapped[list[GovernancePolicy]] = relationship(
        back_populates="project", lazy="raise"
    )
    designs: Mapped[list[Design]] = relationship(
        back_populates="project", lazy="raise"
    )
    evaluations: Mapped[list[Evaluation]] = relationship(
        back_populates="project", lazy="raise"
    )
