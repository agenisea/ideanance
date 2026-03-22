"""Health check endpoint."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from _version import __version__
from database import get_db

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    database: bool
    version: str
    timestamp: str


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        database=db_ok,
        version=__version__,
        timestamp=datetime.now(UTC).isoformat(),
    )
