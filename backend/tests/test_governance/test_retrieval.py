"""Tests for hybrid retrieval and context assembly."""

from sqlalchemy.ext.asyncio import AsyncSession

from ideanance.core.embeddings import EMBEDDING_DIMENSION, EmbeddingClient
from ideanance.modules.governance.chunk_models import GovernanceChunk
from ideanance.modules.governance.constants import (
    CATEGORY_GOVERN,
    CATEGORY_MAP,
    CATEGORY_MEASURE,
    FRAMEWORK_NIST_AI_RMF,
    NIST_GOVERN_1_1,
    NIST_MAP_1_5,
)
from ideanance.modules.governance.context_assembly import ContextAssembler
from ideanance.modules.governance.retrieval import (
    HybridRetriever,
    RetrievalResult,
)


async def _seed_chunks(db: AsyncSession) -> list[GovernanceChunk]:
    """Seed test chunks into DB."""
    chunks = [
        GovernanceChunk(
            content="Design must include a stated purpose for transparency",
            framework=FRAMEWORK_NIST_AI_RMF,
            category=CATEGORY_GOVERN,
            section_id=NIST_GOVERN_1_1,
            section_title="Legal and Regulatory Requirements",
            chunk_type="subcategory",
            token_count=10,
        ),
        GovernanceChunk(
            content="Risk assessment must identify failure modes and threats",
            framework=FRAMEWORK_NIST_AI_RMF,
            category=CATEGORY_MAP,
            section_id=NIST_MAP_1_5,
            section_title="Risk Identification",
            chunk_type="subcategory",
            token_count=10,
        ),
        GovernanceChunk(
            content="Evaluation metrics must be defined before deployment",
            framework=FRAMEWORK_NIST_AI_RMF,
            category=CATEGORY_MEASURE,
            section_id="nist-measure-2.1",
            section_title="Evaluation Metrics Defined",
            chunk_type="subcategory",
            token_count=10,
        ),
    ]
    for c in chunks:
        db.add(c)
    await db.flush()
    return chunks


async def test_keyword_search_finds_relevant_chunks(db: AsyncSession):
    await _seed_chunks(db)
    retriever = HybridRetriever(db=db, is_sqlite=True)

    results = await retriever.search(
        query="purpose transparency",
        frameworks=[FRAMEWORK_NIST_AI_RMF],
    )
    assert len(results) >= 1
    assert any("purpose" in r.content for r in results)


async def test_keyword_search_filters_by_framework(db: AsyncSession):
    await _seed_chunks(db)
    retriever = HybridRetriever(db=db, is_sqlite=True)

    results = await retriever.search(
        query="purpose",
        frameworks=["EU AI Act"],  # No EU AI Act chunks seeded
    )
    assert len(results) == 0


async def test_keyword_search_returns_empty_for_no_match(
    db: AsyncSession,
):
    await _seed_chunks(db)
    retriever = HybridRetriever(db=db, is_sqlite=True)

    results = await retriever.search(
        query="xyznonexistent",
        frameworks=[FRAMEWORK_NIST_AI_RMF],
    )
    assert len(results) == 0


def test_rrf_fusion():
    list_a = [
        RetrievalResult(
            chunk_id="1",
            content="a",
            framework="F",
            category="C",
            section_id="s1",
            section_title="t1",
        ),
        RetrievalResult(
            chunk_id="2",
            content="b",
            framework="F",
            category="C",
            section_id="s2",
            section_title="t2",
        ),
    ]
    list_b = [
        RetrievalResult(
            chunk_id="2",
            content="b",
            framework="F",
            category="C",
            section_id="s2",
            section_title="t2",
        ),
        RetrievalResult(
            chunk_id="3",
            content="c",
            framework="F",
            category="C",
            section_id="s3",
            section_title="t3",
        ),
    ]

    fused = HybridRetriever._reciprocal_rank_fusion(
        list_a, list_b
    )
    # chunk "2" appears in both lists, should rank highest
    assert fused[0].chunk_id == "2"
    # Median threshold may filter low-score results
    assert len(fused) >= 2


async def test_context_assembly_formats_sections(db: AsyncSession):
    assembler = ContextAssembler(db=db)
    results = [
        RetrievalResult(
            chunk_id="1",
            content="Purpose must be stated",
            framework=FRAMEWORK_NIST_AI_RMF,
            category=CATEGORY_GOVERN,
            section_id=NIST_GOVERN_1_1,
            section_title="Legal Requirements",
        ),
        RetrievalResult(
            chunk_id="2",
            content="Risk assessment required",
            framework=FRAMEWORK_NIST_AI_RMF,
            category=CATEGORY_MAP,
            section_id=NIST_MAP_1_5,
            section_title="Risk Identification",
        ),
    ]
    context = await assembler.assemble(results)
    assert NIST_GOVERN_1_1 in context
    assert NIST_MAP_1_5 in context
    assert "---" in context  # Section separator


async def test_context_assembly_deduplicates(db: AsyncSession):
    assembler = ContextAssembler(db=db)
    results = [
        RetrievalResult(
            chunk_id="1",
            content="A",
            framework="F",
            category="C",
            section_id="s1",
            section_title="T",
        ),
        RetrievalResult(
            chunk_id="2",
            content="B",
            framework="F",
            category="C",
            section_id="s1",  # Duplicate section_id
            section_title="T",
        ),
    ]
    context = await assembler.assemble(results)
    # Should only include one section
    assert context.count("[F — s1:") == 1


def test_embedding_client_dummy():
    client = EmbeddingClient()  # No API key
    # Should return dummy embedding synchronously
    dummy = client._dummy_embedding()
    assert len(dummy) == EMBEDDING_DIMENSION
    assert all(v == 0.0 for v in dummy)
