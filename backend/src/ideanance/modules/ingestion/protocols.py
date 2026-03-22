"""Protocol interfaces for ingestion module."""

from __future__ import annotations

from typing import Protocol

from ideanance.modules.governance.chunk_models import GovernanceChunk


class GovernanceChunkRepo(Protocol):
    async def create(self, **kwargs: object) -> GovernanceChunk: ...
    async def count_by_framework(self, framework: str) -> int: ...
    async def list_by_framework(
        self, framework: str
    ) -> list[GovernanceChunk]: ...
    async def delete_by_framework(
        self, framework: str
    ) -> int: ...
