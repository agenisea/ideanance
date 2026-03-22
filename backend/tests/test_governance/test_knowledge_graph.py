"""Tests for knowledge graph and graph builder — PLAN36."""

from pathlib import Path

from modules.governance.constants import (
    FRAMEWORK_EU_AI_ACT,
    FRAMEWORK_NIST_AI_RMF,
    NIST_GOVERN_1_4,
    NIST_MANAGE_2_1,
)
from modules.governance.knowledge_graph import GraphEdge, KnowledgeGraph
from modules.ingestion.graph_builder import KnowledgeGraphLoader

CROSS_MAPPINGS_DIR = (
    Path(__file__).resolve().parents[3] / "governance-policies" / "cross_mappings"
)


def _make_test_graph() -> KnowledgeGraph:
    edges = [
        GraphEdge(
            source_id=NIST_GOVERN_1_4,
            source_framework=FRAMEWORK_NIST_AI_RMF,
            target_id="eu-art9-risk-management",
            target_framework=FRAMEWORK_EU_AI_ACT,
            relationship="overlap",
        ),
        GraphEdge(
            source_id=NIST_MANAGE_2_1,
            source_framework=FRAMEWORK_NIST_AI_RMF,
            target_id="eu-art14-human-oversight",
            target_framework=FRAMEWORK_EU_AI_ACT,
            relationship="equivalent",
        ),
    ]
    return KnowledgeGraph(edges=edges)


def test_knowledge_graph_get_related_from_source():
    graph = _make_test_graph()
    related = graph.get_related(NIST_GOVERN_1_4)
    assert len(related) == 1
    assert related[0].target_id == "eu-art9-risk-management"


def test_knowledge_graph_get_related_from_target():
    graph = _make_test_graph()
    related = graph.get_related("eu-art14-human-oversight")
    assert len(related) == 1
    assert related[0].source_id == NIST_MANAGE_2_1


def test_knowledge_graph_no_related():
    graph = _make_test_graph()
    related = graph.get_related("nonexistent-id")
    assert len(related) == 0


def test_knowledge_graph_expand_context():
    graph = _make_test_graph()
    expanded = graph.expand_context([NIST_GOVERN_1_4])
    assert NIST_GOVERN_1_4 in expanded
    assert "eu-art9-risk-management" in expanded


def test_knowledge_graph_expand_multiple():
    graph = _make_test_graph()
    expanded = graph.expand_context([NIST_GOVERN_1_4, NIST_MANAGE_2_1])
    assert len(expanded) == 4  # 2 original + 2 expanded
    assert "eu-art9-risk-management" in expanded
    assert "eu-art14-human-oversight" in expanded


def test_knowledge_graph_expand_no_duplicates():
    graph = _make_test_graph()
    expanded = graph.expand_context([NIST_GOVERN_1_4, "eu-art9-risk-management"])
    # eu-art9 is both in input and expandable from nist-govern-1.4
    # Should not duplicate
    assert expanded.count("eu-art9-risk-management") <= 1


def test_knowledge_graph_max_depth_zero():
    graph = _make_test_graph()
    related = graph.get_related(NIST_GOVERN_1_4, max_depth=0)
    assert len(related) == 0


def test_knowledge_graph_edge_count():
    graph = _make_test_graph()
    assert graph.edge_count == 2


def test_empty_knowledge_graph():
    graph = KnowledgeGraph()
    assert graph.edge_count == 0
    assert graph.expand_context(["anything"]) == ["anything"]


# --- KnowledgeGraphLoader tests ---


def test_loader_loads_cross_mappings_yaml():
    loader = KnowledgeGraphLoader()
    graph = loader.load_all(CROSS_MAPPINGS_DIR)
    assert graph.edge_count >= 5
    related = graph.get_related(NIST_GOVERN_1_4)
    assert len(related) >= 1
    assert any(
        e.target_id == "eu-art9-risk-management" for e in related
    )


def test_loader_handles_missing_directory():
    loader = KnowledgeGraphLoader()
    graph = loader.load_all(Path("/nonexistent/path"))
    assert graph.edge_count == 0


def test_loader_loads_single_file():
    loader = KnowledgeGraphLoader()
    yml_file = CROSS_MAPPINGS_DIR / "nist_eu_ai_act.yml"
    graph = loader.load_from_yaml(yml_file)
    assert graph.edge_count >= 5
