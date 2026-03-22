"""GovernanceChunk model for RAG retrieval.

Cross-DB strategy: embedding column is Text (JSON-serialized floats) on SQLite,
Vector(1536) on PostgreSQL. The retrieval layer handles the difference.
On SQLite, retrieval falls back to keyword-only search.
"""

from __future__ import annotations

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class GovernanceChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Embedded governance policy chunk for RAG retrieval."""

    __tablename__ = "governance_chunks"

    content: Mapped[str] = mapped_column(Text)
    framework: Mapped[str] = mapped_column(String(100), index=True)
    category: Mapped[str] = mapped_column(String(100))
    section_id: Mapped[str] = mapped_column(String(100), index=True)
    section_title: Mapped[str] = mapped_column(String(255))
    parent_chunk_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True
    )
    chunk_type: Mapped[str] = mapped_column(String(50))
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    chunk_metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    # Embedding stored as JSON text for SQLite compat.
    # On PostgreSQL with pgvector, migrate to Vector(1536) column.
    embedding_json: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
