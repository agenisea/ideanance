"""Tests for query rewriter — PLAN36."""

from modules.governance.constants import (
    FRAMEWORK_EU_AI_ACT,
    FRAMEWORK_NIST_AI_RMF,
)
from modules.governance.query_rewriter import QueryRewriter


def test_rewriter_returns_original_query():
    rewriter = QueryRewriter()
    queries = rewriter.rewrite("risk management", [FRAMEWORK_NIST_AI_RMF])
    assert queries[0] == "risk management"


def test_rewriter_expands_abbreviations():
    rewriter = QueryRewriter()
    queries = rewriter.rewrite("TEVV requirements", [FRAMEWORK_NIST_AI_RMF])
    assert any("test evaluation verification validation" in q for q in queries)


def test_rewriter_expands_rmf_abbreviation():
    rewriter = QueryRewriter()
    queries = rewriter.rewrite("RMF compliance", [FRAMEWORK_NIST_AI_RMF])
    assert any("risk management framework" in q for q in queries)


def test_rewriter_adds_framework_terms():
    rewriter = QueryRewriter()
    queries = rewriter.rewrite(
        "risk management",
        [FRAMEWORK_NIST_AI_RMF, FRAMEWORK_EU_AI_ACT],
    )
    # Should add NIST-specific terms
    assert any("govern" in q for q in queries)
    # Should add EU-specific terms
    assert any("article 9" in q for q in queries)


def test_rewriter_no_expansion_for_unknown_topic():
    rewriter = QueryRewriter()
    queries = rewriter.rewrite(
        "quantum computing",
        [FRAMEWORK_NIST_AI_RMF],
    )
    # Only original query, no expansion
    assert len(queries) == 1


def test_rewriter_multi_framework_transparency():
    rewriter = QueryRewriter()
    queries = rewriter.rewrite(
        "transparency",
        [FRAMEWORK_NIST_AI_RMF, FRAMEWORK_EU_AI_ACT],
    )
    assert any("article 50" in q or "disclosure" in q for q in queries)
    assert any("documentation" in q for q in queries)
