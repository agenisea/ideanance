"""CustomFramework SQLAlchemy model — greenfield, no migration."""

from __future__ import annotations

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class CustomFrameworkModel(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    """User-created governance framework persisted to DB."""

    __tablename__ = "custom_frameworks"

    framework_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True
    )
    project_id: Mapped[str] = mapped_column(
        String(36), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(
        String(50), default="1.0.0"
    )
    description: Mapped[str] = mapped_column(
        Text, default=""
    )
    categories: Mapped[dict] = mapped_column(
        JSON, default=list
    )
