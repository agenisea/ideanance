"""Knowledge graph loader — I/O layer.

Loads cross-mapping YAML files and constructs a KnowledgeGraph.
Separated from KnowledgeGraph (pure data) per clean architecture.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from modules.governance.knowledge_graph import GraphEdge, KnowledgeGraph


class KnowledgeGraphLoader:
    """Loads cross-mapping YAML files and constructs a KnowledgeGraph."""

    def load_from_yaml(self, path: Path) -> KnowledgeGraph:
        """Parse a single cross-mapping YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)

        edges = [
            GraphEdge(
                source_id=m["source_id"],
                source_framework=m["source_framework"],
                target_id=m["target_id"],
                target_framework=m["target_framework"],
                relationship=m["relationship"],
                description=m.get("description", ""),
            )
            for m in data.get("mappings", [])
        ]
        return KnowledgeGraph(edges=edges)

    def load_all(self, cross_mappings_dir: Path) -> KnowledgeGraph:
        """Load all cross-mapping YAML files from a directory."""
        all_edges: list[GraphEdge] = []
        if not cross_mappings_dir.exists():
            return KnowledgeGraph(edges=[])
        for yml_file in sorted(cross_mappings_dir.glob("*.yml")):
            graph = self.load_from_yaml(yml_file)
            all_edges.extend(graph._edges)
        return KnowledgeGraph(edges=all_edges)
