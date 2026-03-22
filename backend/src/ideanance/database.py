"""SQLAlchemy async engine and session factory."""

from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ideanance.config import settings

_engine_kwargs: dict = {}
if not settings.is_sqlite:
    _engine_kwargs = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    **_engine_kwargs,
)

# Enable foreign key enforcement for SQLite
if settings.is_sqlite:

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session."""
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()
