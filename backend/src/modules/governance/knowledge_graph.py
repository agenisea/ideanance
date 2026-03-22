"""In-memory cross-framework relationship graph.

Pure data structure — no I/O. Receives edges via constructor.
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass(frozen=True)
class GraphEdge:
    """A relationship between two governance sections across frameworks."""

    source_id: str
    source_framework: str
    target_id: str
    target_framework: str
    relationship: str  # "overlap" | "equivalent" | "subset" | "partial"
    description: str = ""


class KnowledgeGraph:
    """In-memory cross-framework relationship graph.

    Receives edges via constructor. Supports single-hop traversal only.
    Multi-hop expansion (depth > 1) deferred to Phase 3 with reranker.
    """

    def __init__(self, edges: list[GraphEdge] | None = None) -> None:
        self._edges = edges or []
        self._by_source: dict[str, list[GraphEdge]] = {}
        self._by_target: dict[str, list[GraphEdge]] = {}
        for edge in self._edges:
            self._by_source.setdefault(edge.source_id, []).append(edge)
            self._by_target.setdefault(edge.target_id, []).append(edge)

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    def get_related(
        self, section_id: str, max_depth: int = 1
    ) -> list[GraphEdge]:
        """Find related sections across frameworks.

        Phase 2 caps max_depth=1. Multi-hop requires a reranker (Phase 3).
        """
        if max_depth < 1:
            return []

        related: list[GraphEdge] = []
        # Bidirectional: check both source and target
        related.extend(self._by_source.get(section_id, []))
        related.extend(self._by_target.get(section_id, []))
        return related

    def expand_context(self, section_ids: list[str]) -> list[str]:
        """Given retrieved section IDs, add cross-framework related IDs.

        Uses single-hop expansion only (max_depth=1).
        Returns deduplicated list of all section IDs including expansions.
        """
        log.info(
            "knowledge_graph.expanding",
            input_count=len(section_ids),
        )
        all_ids = set(section_ids)
        for sid in section_ids:
            for edge in self.get_related(sid, max_depth=1):
                # Add the "other" side of the edge
                if edge.source_id == sid:
                    all_ids.add(edge.target_id)
                else:
                    all_ids.add(edge.source_id)
        return list(all_ids)
