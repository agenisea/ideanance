"""GovernanceLens Protocol — independent evaluators."""

from __future__ import annotations

from typing import Any, Protocol

from modules.governance.loader import LoadedPolicy
from modules.governance.verdict import LensResult


class GovernanceLens(Protocol):
    """Independent evaluator for one governance concern."""

    @property
    def name(self) -> str: ...

    def evaluate(
        self,
        artifact: dict[str, Any],
        policies: list[LoadedPolicy],
    ) -> LensResult: ...


# Policy-to-lens mapping defaults (from category)
CATEGORY_LENS_MAP: dict[str, list[str]] = {
    "govern": ["boundary", "accountability"],
    "map": ["boundary", "transparency"],
    "measure": ["transparency", "privacy"],
    "manage": ["accountability", "boundary"],
    "prohibited": ["dignity", "boundary"],
    "high-risk": [
        "boundary",
        "transparency",
        "accountability",
        "privacy",
        "dignity",
    ],
    "limited": ["transparency"],
    "transparency": ["transparency"],
    "data": ["privacy"],
}


def get_lens_names_for_policy(
    policy: LoadedPolicy,
) -> list[str]:
    """Get lens names for a policy.

    Uses governance_concerns from YAML if present,
    otherwise falls back to category mapping.
    """
    # Future: read from policy YAML governance_concerns
    return CATEGORY_LENS_MAP.get(
        policy.category, ["boundary"]
    )
