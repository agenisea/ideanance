"""Evaluation models: eval suites and criteria with governance wiring."""

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
from modules.evaluation.constants import EVAL_STATUS_DRAFT

if TYPE_CHECKING:
    from modules.governance.models import (
        GovernanceEvalWiring,
        GovernancePolicy,
    )
    from modules.workspace.models import Project


class Evaluation(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """A collection of eval criteria for a project."""

    __tablename__ = "evaluations"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id"), index=True
    )
    design_id: Mapped[str | None] = mapped_column(
        ForeignKey("designs.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default=EVAL_STATUS_DRAFT)

    project: Mapped[Project] = relationship(back_populates="evaluations")
    criteria: Mapped[list[EvalCriterion]] = relationship(
        back_populates="evaluation", lazy="raise"
    )


class EvalCriterion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single evaluation criterion, wirable to governance policies."""

    __tablename__ = "eval_criteria"

    evaluation_id: Mapped[str] = mapped_column(
        ForeignKey("evaluations.id"), index=True
    )
    criterion_id: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    metric: Mapped[str] = mapped_column(String(255))
    threshold: Mapped[str] = mapped_column(String(255))
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    test_cases: Mapped[dict] = mapped_column(JSON, default=dict)

    evaluation: Mapped[Evaluation] = relationship(back_populates="criteria")
    wirings: Mapped[list[GovernanceEvalWiring]] = relationship(
        back_populates="criterion", lazy="raise"
    )

    # Bidirectional traversal: criterion -> governance policies (via wiring table)
    governance_policies: Mapped[list[GovernancePolicy]] = relationship(
        secondary="governance_eval_wirings",
        back_populates="eval_criteria",
        viewonly=True,
        lazy="raise",
    )
