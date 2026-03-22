"""Design models: agent and pipeline design artifacts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from modules.workspace.models import Project


class Design(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """An agent or pipeline design artifact within a project."""

    __tablename__ = "designs"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    design_type: Mapped[str] = mapped_column(String(50))
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)

    project: Mapped[Project] = relationship(back_populates="designs")
