"""Governance lenses — independent evaluators per concern.

Each lens implements the GovernanceLens protocol from base.py.
Use create_lenses() factory for the standard 5-lens set.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from modules.governance.lenses.accountability import (
    AccountabilityLens,
)
from modules.governance.lenses.boundary import (
    BoundaryLens,
)
from modules.governance.lenses.dignity import (
    DignityLens,
)
from modules.governance.lenses.privacy import (
    PrivacyLens,
)
from modules.governance.lenses.transparency import (
    TransparencyLens,
)

if TYPE_CHECKING:
    from modules.governance.engine import GovernanceEngine
    from modules.governance.lenses.base import (
        GovernanceLens,
    )

__all__ = [
    "AccountabilityLens",
    "BoundaryLens",
    "DignityLens",
    "PrivacyLens",
    "TransparencyLens",
    "create_lenses",
]


def create_lenses(
    engine: GovernanceEngine | None = None,
) -> list[GovernanceLens]:
    """Factory for the standard 5-lens governance set.

    Args:
        engine: Optional GovernanceEngine for dependency injection.
                If None, each lens creates its own engine lazily.

    Returns:
        List of all 5 governance lenses.
    """
    return [
        BoundaryLens(engine=engine),
        TransparencyLens(engine=engine),
        AccountabilityLens(engine=engine),
        PrivacyLens(engine=engine),
        DignityLens(engine=engine),
    ]
