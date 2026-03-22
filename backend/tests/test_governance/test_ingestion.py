"""Tests for ingestion module: chunker, service, seeder."""

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from ideanance.core.embeddings import EmbeddingClient
from ideanance.modules.governance.constants import (
    FRAMEWORK_NIST_AI_RMF,
    NIST_GOVERN_1_1,
)
from ideanance.modules.governance.loader import load_policy_file
from ideanance.modules.ingestion.chunker import GovernanceChunker
from ideanance.modules.ingestion.repository import (
    SqlGovernanceChunkRepository,
)
from ideanance.modules.ingestion.seeder import NIST_DIR, FrameworkSeeder
from ideanance.modules.ingestion.service import IngestionService

FIXTURE_PATH = (
    Path(__file__).resolve().parents[3]
    / "governance-policies"
    / "nist-ai-rmf"
    / "govern"
    / "govern-1-1.yml"
)


def test_chunker_produces_main_and_remediation():
    policy = load_policy_file(FIXTURE_PATH)
    chunker = GovernanceChunker()
    chunks = chunker.chunk_policy(policy)

    # Parent + 3 rules + remediation = 5 chunks
    assert len(chunks) >= 4
    parent = chunks[0]
    assert parent.chunk_type == "subcategory"
    assert parent.section_id == NIST_GOVERN_1_1

    # Rule chunks follow parent
    rule_chunks = [c for c in chunks if c.chunk_type == "rule"]
    assert len(rule_chunks) >= 2
    assert all(
        c.parent_chunk_id == NIST_GOVERN_1_1
        for c in rule_chunks
    )

    # Remediation
    remed = [c for c in chunks if c.chunk_type == "remediation"]
    assert len(remed) == 1
    assert remed[0].parent_chunk_id == NIST_GOVERN_1_1


def test_chunker_all_policies():
    from ideanance.modules.governance.loader import (
        load_framework_policies,
    )

    policies = load_framework_policies(NIST_DIR)
    chunker = GovernanceChunker()
    total_chunks = 0
    for p in policies:
        chunks = chunker.chunk_policy(p)
        assert len(chunks) >= 1
        total_chunks += len(chunks)
    # 20 policies * (parent + ~3 rules + remediation) = ~100 chunks
    assert total_chunks >= 80


async def test_ingestion_service_seeds_framework(db: AsyncSession):
    chunk_repo = SqlGovernanceChunkRepository(db)
    embedding_client = EmbeddingClient()  # Dummy (no API key)
    chunker = GovernanceChunker()

    svc = IngestionService(
        chunk_repo=chunk_repo,
        embedding_client=embedding_client,
        chunker=chunker,
    )

    count = await svc.seed_framework(NIST_DIR)
    assert count >= 80  # 20 policies * ~4 chunks each

    # Verify chunks in DB
    db_count = await chunk_repo.count_by_framework(FRAMEWORK_NIST_AI_RMF)
    assert db_count == count


async def test_seeder_idempotent(db: AsyncSession):
    chunk_repo = SqlGovernanceChunkRepository(db)
    embedding_client = EmbeddingClient()
    chunker = GovernanceChunker()
    svc = IngestionService(
        chunk_repo=chunk_repo,
        embedding_client=embedding_client,
        chunker=chunker,
    )
    seeder = FrameworkSeeder(
        ingestion_service=svc, chunk_repo=chunk_repo
    )

    # First seed
    count1 = await seeder.seed_if_needed()
    assert count1 > 0

    # Second seed — should skip (idempotent)
    count2 = await seeder.seed_if_needed()
    assert count2 == 0
