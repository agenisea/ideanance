"""Optional JWT auth: disabled for local dev, enabled for hosted deployment."""

from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ideanance.config import settings

security = HTTPBearer(auto_error=False)


async def get_current_user(
    token: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict | None:
    """Authenticate request. Returns None when auth is disabled (local dev)."""
    if not settings.enable_auth:
        return None  # Auth disabled for local dev

    if token is None:
        raise HTTPException(401, "Not authenticated")

    try:
        import jwt as pyjwt

        payload = pyjwt.decode(
            token.credentials,
            settings.secret_key,
            algorithms=["HS256"],
        )
        return payload  # type: ignore[return-value]
    except Exception:
        raise HTTPException(401, "Invalid token") from None
