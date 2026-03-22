"""Governance models: policies, checks, and the governance-eval wiring join table."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ideanance.models.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from ideanance.modules.evaluation.models import EvalCriterion
    from ideanance.modules.workspace.models import Project


class GovernancePolicy(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """A governance policy attached to a project."""

    __tablename__ = "governance_policies"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id"), index=True
    )
    framework: Mapped[str] = mapped_column(String(100))
    policy_id: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100))
    subcategory: Mapped[str] = mapped_column(String(100), default="")
    severity: Mapped[str] = mapped_column(String(20), default="warning")
    rules: Mapped[dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(default=True)

    project: Mapped[Project] = relationship(back_populates="governance_policies")
    wirings: Mapped[list[GovernanceEvalWiring]] = relationship(
        back_populates="policy",
        lazy="raise",
        cascade="all, delete-orphan",
    )
    checks: Mapped[list[GovernanceCheck]] = relationship(
        back_populates="policy", lazy="raise"
    )

    # --- Aggregate methods ---

    def deactivate(self) -> None:
        """Domain method — policy deactivates itself."""
        self.enabled = False

    def activate(self) -> None:
        """Domain method — policy activates itself."""
        self.enabled = True

    def is_active(self) -> bool:
        """Check if policy is active and not deleted."""
        return self.enabled and self.deleted_at is None

    # Bidirectional traversal: policy -> eval criteria (via wiring table)
    eval_criteria: Mapped[list[EvalCriterion]] = relationship(
        secondary="governance_eval_wirings",
        back_populates="governance_policies",
        viewonly=True,
        lazy="raise",
    )


class GovernanceEvalWiring(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Links a governance policy to an evaluation criterion.

    This is the atomic unit of a Governance-Wired Project.
    """

    __tablename__ = "governance_eval_wirings"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id"), index=True
    )
    policy_id: Mapped[str] = mapped_column(
        ForeignKey("governance_policies.id"), index=True
    )
    criterion_id: Mapped[str] = mapped_column(
        ForeignKey("eval_criteria.id"), index=True
    )
    wiring_type: Mapped[str] = mapped_column(String(20), default="manual")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    rationale: Mapped[str] = mapped_column(Text, default="")

    policy: Mapped[GovernancePolicy] = relationship(back_populates="wirings")
    criterion: Mapped[EvalCriterion] = relationship(back_populates="wirings")


class GovernanceCheck(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Result of running governance checks against a design."""

    __tablename__ = "governance_checks"

    design_id: Mapped[str] = mapped_column(
        ForeignKey("designs.id"), index=True
    )
    policy_id: Mapped[str] = mapped_column(
        ForeignKey("governance_policies.id"), index=True
    )
    results: Mapped[dict] = mapped_column(JSON, default=dict)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20))

    policy: Mapped[GovernancePolicy] = relationship(back_populates="checks")
