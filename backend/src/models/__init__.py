"""SQLAlchemy models — base re-exports.

Module models are imported lazily in main.py lifespan to avoid circular imports.
"""

from models.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

__all__ = [
    "Base",
    "UUIDPrimaryKeyMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
]


def import_all_models() -> None:
    """Import all module models so SQLAlchemy resolves relationships.

    Call this once at startup (in lifespan) before create_all or migrations.
    """
    import modules.analytics.models  # noqa: F401
    import modules.design.models  # noqa: F401
    import modules.evaluation.models  # noqa: F401
    import modules.governance.audit  # noqa: F401
    import modules.governance.chunk_models  # noqa: F401
    import modules.governance.custom_framework_models  # noqa: F401
    import modules.governance.models  # noqa: F401
    import modules.workspace.models  # noqa: F401
