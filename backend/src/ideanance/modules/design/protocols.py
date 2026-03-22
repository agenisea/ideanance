"""Protocol interfaces for design repositories."""

from __future__ import annotations

from typing import Protocol

from ideanance.core.constants import DEFAULT_LIST_LIMIT
from ideanance.modules.design.models import Design


class DesignRepo(Protocol):
    async def create(
        self, project_id: str, **kwargs: object
    ) -> Design: ...
    async def get_by_id(self, design_id: str) -> Design | None: ...
    async def list_by_project(
        self, project_id: str, limit: int = DEFAULT_LIST_LIMIT
    ) -> list[Design]: ...
    async def update(
        self, design_id: str, **kwargs: object
    ) -> Design | None: ...
