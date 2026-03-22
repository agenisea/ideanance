"""Protocol interfaces for governance repositories and services."""

from __future__ import annotations

from typing import Protocol

from ideanance.modules.governance.models import (
    GovernanceCheck,
    GovernanceEvalWiring,
    GovernancePolicy,
)


class GovernancePolicyRepo(Protocol):
    async def create(
        self, project_id: str, **kwargs: object
    ) -> GovernancePolicy: ...
    async def get_by_id(
        self, policy_id: str
    ) -> GovernancePolicy | None: ...
    async def list_by_project(
        self, project_id: str, enabled_only: bool = True
    ) -> list[GovernancePolicy]: ...
    async def find_by_policy_id(
        self, project_id: str, policy_id: str
    ) -> GovernancePolicy | None: ...
    async def update_enabled(
        self, policy_id: str, enabled: bool
    ) -> None: ...


class GovernanceEvalWiringRepo(Protocol):
    async def create(
        self, project_id: str, **kwargs: object
    ) -> GovernanceEvalWiring: ...
    async def list_by_project(
        self, project_id: str
    ) -> list[GovernanceEvalWiring]: ...
    async def count_by_project(self, project_id: str) -> int: ...
    async def delete(self, wiring_id: str) -> bool: ...


class GovernanceCheckRepo(Protocol):
    async def create(self, **kwargs: object) -> GovernanceCheck: ...


class QueryRewriterProtocol(Protocol):
    """Rewrites and expands queries for improved governance retrieval."""

    def rewrite(self, query: str, frameworks: list[str]) -> list[str]: ...


class KnowledgeGraphProtocol(Protocol):
    """Provides cross-framework relationship traversal."""

    def get_related(
        self, section_id: str, max_depth: int = 1
    ) -> list: ...

    def expand_context(self, section_ids: list[str]) -> list[str]: ...
