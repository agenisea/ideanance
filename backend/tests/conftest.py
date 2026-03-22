"""Shared test fixtures: in-memory SQLite, async session, FastAPI test client."""

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic_ai import models as pydantic_ai_models
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ideanance.models import Base, import_all_models

import_all_models()

# Safety: block real LLM API calls in all tests
pydantic_ai_models.ALLOW_MODEL_REQUESTS = False


@pytest.fixture
async def engine():
    eng = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest.fixture
async def db(engine) -> AsyncSession:
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(engine):
    """API test client using a shared connection so all requests see the same data."""
    from ideanance.database import get_db
    from ideanance.main import app

    # Use a single connection for all requests in a test so in-memory SQLite
    # shares state across sessions (each session binds to this connection).
    async with engine.connect() as connection:
        # Begin a savepoint we can roll back at the end
        await connection.begin()

        factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async def override_get_db():
            async with factory() as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as c:
            yield c

        await connection.rollback()
        app.dependency_overrides.clear()
