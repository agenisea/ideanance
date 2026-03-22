"""Tests for base model mixins: UUID v7, timestamps, soft delete."""

from datetime import UTC, datetime

from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from models.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class _TestEntity(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "test_entities"
    name: Mapped[str] = mapped_column(String(100))


async def test_uuid_v7_primary_key(db: AsyncSession):
    entity = _TestEntity(name="test")
    db.add(entity)
    await db.flush()

    assert entity.id is not None
    assert len(entity.id) == 36
    assert "-" in entity.id


async def test_timestamps_set_on_create(db: AsyncSession):
    entity = _TestEntity(name="test")
    db.add(entity)
    await db.flush()

    assert entity.created_at is not None
    assert entity.updated_at is not None
    assert isinstance(entity.created_at, datetime)


async def test_soft_delete_mixin(db: AsyncSession):
    entity = _TestEntity(name="test")
    db.add(entity)
    await db.flush()

    assert entity.is_deleted is False
    assert entity.deleted_at is None

    entity.deleted_at = datetime.now(UTC)
    await db.flush()

    assert entity.is_deleted is True
