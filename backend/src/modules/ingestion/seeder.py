"""Framework seeder — seeds governance frameworks on first deployment.

Constructor-injected per PLAN7_REFACTOR patterns.
No raw AsyncSession in method params.
"""

from __future__ import annotations

from pathlib import Path

from modules.governance.constants import (
    FRAMEWORK_EU_AI_ACT,
    FRAMEWORK_ID_EU_AI_ACT,
    FRAMEWORK_ID_NIST_AI_RMF,
    FRAMEWORK_NIST_AI_RMF,
)
from modules.ingestion.protocols import GovernanceChunkRepo
from modules.ingestion.service import IngestionService

_GOVERNANCE_POLICIES_DIR = (
    Path(__file__).resolve().parents[4] / "governance-policies"
)
NIST_DIR = _GOVERNANCE_POLICIES_DIR / FRAMEWORK_ID_NIST_AI_RMF
EU_AI_ACT_DIR = _GOVERNANCE_POLICIES_DIR / FRAMEWORK_ID_EU_AI_ACT


class FrameworkSeeder:
    """Seeds governance frameworks into DB on first deployment."""

    def __init__(
        self,
        ingestion_service: IngestionService,
        chunk_repo: GovernanceChunkRepo,
    ) -> None:
        self.ingestion_service = ingestion_service
        self.chunk_repo = chunk_repo

    async def seed_if_needed(self) -> int:
        """Seed all built-in frameworks if not already seeded."""
        total = 0
        total += await self._seed_framework_if_needed(
            FRAMEWORK_NIST_AI_RMF, NIST_DIR
        )
        total += await self._seed_framework_if_needed(
            FRAMEWORK_EU_AI_ACT, EU_AI_ACT_DIR
        )
        return total

    async def _seed_framework_if_needed(
        self, framework_name: str, framework_dir: Path
    ) -> int:
        """Seed a framework if not already seeded."""
        count = await self.chunk_repo.count_by_framework(framework_name)
        if count > 0:
            return 0
        return await self.ingestion_service.seed_framework(framework_dir)

    async def seed_nist_ai_rmf(self) -> int:
        """Seed the NIST AI RMF framework."""
        return await self.ingestion_service.seed_framework(NIST_DIR)

    async def seed_eu_ai_act(self) -> int:
        """Seed the EU AI Act framework."""
        return await self.ingestion_service.seed_framework(EU_AI_ACT_DIR)
