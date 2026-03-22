"""Cross-framework mapping — loads and queries cross-references between frameworks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import structlog
import yaml

log = structlog.get_logger()


@dataclass(frozen=True)
class CrossMapping:
    """A mapping between policies in different frameworks."""

    source_id: str
    source_framework: str
    target_id: str
    target_framework: str
    relationship: str  # "overlap" | "equivalent" | "subset" | "partial"
    description: str = ""


class CrossFrameworkMapper:
    """Maps controls/articles between governance frameworks.

    Loads cross-mapping data from YAML files.
    """

    def __init__(self, mappings: list[CrossMapping] | None = None) -> None:
        self._mappings = mappings or []

    @classmethod
    def from_yaml_dir(cls, cross_mappings_dir: Path) -> CrossFrameworkMapper:
        """Load all cross-mapping YAML files from a directory."""
        log.info(
            "cross_mapping.loading",
            dir=str(cross_mappings_dir),
        )
        mappings: list[CrossMapping] = []
        if not cross_mappings_dir.exists():
            return cls(mappings=[])
        for yml_file in sorted(cross_mappings_dir.glob("*.yml")):
            with open(yml_file) as f:
                data = yaml.safe_load(f)
            for m in data.get("mappings", []):
                mappings.append(
                    CrossMapping(
                        source_id=m["source_id"],
                        source_framework=m["source_framework"],
                        target_id=m["target_id"],
                        target_framework=m["target_framework"],
                        relationship=m["relationship"],
                        description=m.get("description", ""),
                    )
                )
        return cls(mappings=mappings)

    def get_mappings(
        self,
        framework_a: str,
        framework_b: str,
    ) -> list[CrossMapping]:
        """Get all mappings between two frameworks (bidirectional)."""
        return [
            m
            for m in self._mappings
            if (
                (
                    m.source_framework == framework_a
                    and m.target_framework == framework_b
                )
                or (
                    m.source_framework == framework_b
                    and m.target_framework == framework_a
                )
            )
        ]

    def get_all_mappings(self) -> list[CrossMapping]:
        return list(self._mappings)

    @property
    def mapping_count(self) -> int:
        return len(self._mappings)
