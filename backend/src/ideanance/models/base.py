"""SQLAlchemy declarative base and shared mixins.

Design decisions (from PLAN2 + PLAN3):
- String(36) UUIDs for SQLite + PostgreSQL cross-compat
- Python-side datetime defaults (not server_default) for SQLite compat
- AsyncAttrs for safe async relationship access
- SoftDeleteMixin for governance audit trail
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid_utils import uuid7


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _new_uuid() -> str:
    return str(uuid7())


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all Ideanance SQLAlchemy models."""

    pass


class UUIDPrimaryKeyMixin:
    """Mixin providing a UUID v7 primary key as String(36)."""

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=_new_uuid,
    )


class TimestampMixin:
    """Mixin providing created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
    )


class SoftDeleteMixin:
    """Mixin providing soft delete via deleted_at timestamp."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
