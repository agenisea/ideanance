"""Agent streaming endpoint with SSE."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentRunRequest(BaseModel):
    workspace_id: str
    project_id: str
    prompt: str = Field(min_length=1, max_length=10000)


@router.post("/{agent_id}/run")
async def run_agent(
    agent_id: str,
    request: AgentRunRequest,
) -> dict[str, Any]:
    """Run an agent (non-streaming for now).

    Full SSE streaming will be wired when agents connect to
    real models. For testing, returns a placeholder.
    """
    # Placeholder — full streaming in production requires
    # GovernanceDeps construction from dependencies.py
    return {
        "agent_id": agent_id,
        "status": "placeholder",
        "message": (
            "Agent streaming endpoint ready. "
            "Connect with real models to enable SSE."
        ),
    }
