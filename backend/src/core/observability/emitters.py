"""Typed emitter convenience functions for trace events."""

from __future__ import annotations

from core.observability.dispatcher import TraceDispatcher
from core.observability.events import TraceEvent


async def emit_agent_start(
    dispatcher: TraceDispatcher,
    trace_id: str,
    agent_id: str,
    model: str,
) -> None:
    """Emit an agent_start trace event."""
    await dispatcher.emit(
        TraceEvent(
            type="agent_start",
            trace_id=trace_id,
            category="agent",
            data={
                "agent_id": agent_id,
                "model": model,
            },
        )
    )


async def emit_agent_end(
    dispatcher: TraceDispatcher,
    trace_id: str,
    agent_id: str,
    duration_ms: float,
    success: bool,
) -> None:
    """Emit an agent_end trace event."""
    await dispatcher.emit(
        TraceEvent(
            type="agent_end",
            trace_id=trace_id,
            category="agent",
            data={
                "agent_id": agent_id,
                "duration_ms": duration_ms,
                "success": success,
            },
        )
    )


async def emit_pipeline_start(
    dispatcher: TraceDispatcher,
    trace_id: str,
    workspace_id: str,
    query: str,
) -> None:
    """Emit a pipeline_start trace event."""
    await dispatcher.emit(
        TraceEvent(
            type="pipeline_start",
            trace_id=trace_id,
            category="pipeline",
            data={
                "workspace_id": workspace_id,
                "query": query,
            },
        )
    )


async def emit_pipeline_end(
    dispatcher: TraceDispatcher,
    trace_id: str,
    duration_ms: float,
    success: bool,
) -> None:
    """Emit a pipeline_end trace event."""
    await dispatcher.emit(
        TraceEvent(
            type="pipeline_end",
            trace_id=trace_id,
            category="pipeline",
            data={
                "duration_ms": duration_ms,
                "success": success,
            },
        )
    )


async def emit_governance_eval(
    dispatcher: TraceDispatcher,
    trace_id: str,
    policy_count: int,
    lens_count: int,
    findings_count: int,
) -> None:
    """Emit a governance_eval_end trace event."""
    await dispatcher.emit(
        TraceEvent(
            type="governance_eval_end",
            trace_id=trace_id,
            category="governance",
            data={
                "policy_count": policy_count,
                "lens_count": lens_count,
                "findings_count": findings_count,
            },
        )
    )


async def emit_llm_call(
    dispatcher: TraceDispatcher,
    trace_id: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    duration_ms: float,
    cost: float,
) -> None:
    """Emit an llm_call trace event."""
    await dispatcher.emit(
        TraceEvent(
            type="llm_call",
            trace_id=trace_id,
            category="llm",
            data={
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "duration_ms": duration_ms,
                "cost": cost,
            },
        )
    )


async def emit_handoff(
    dispatcher: TraceDispatcher,
    trace_id: str,
    from_agent: str,
    to_agent: str,
    reason: str,
) -> None:
    """Emit a handoff trace event."""
    await dispatcher.emit(
        TraceEvent(
            type="handoff",
            trace_id=trace_id,
            category="agent",
            data={
                "from_agent": from_agent,
                "to_agent": to_agent,
                "reason": reason,
            },
        )
    )


async def emit_fallback(
    dispatcher: TraceDispatcher,
    trace_id: str,
    agent_id: str,
    level: str,
    reason: str,
) -> None:
    """Emit a fallback trace event."""
    await dispatcher.emit(
        TraceEvent(
            type="fallback",
            trace_id=trace_id,
            category="agent",
            data={
                "agent_id": agent_id,
                "level": level,
                "reason": reason,
            },
        )
    )


async def emit_error(
    dispatcher: TraceDispatcher,
    trace_id: str,
    component: str,
    message: str,
) -> None:
    """Emit an error trace event."""
    await dispatcher.emit(
        TraceEvent(
            type="error",
            trace_id=trace_id,
            category="agent",
            data={
                "component": component,
                "message": message,
            },
        )
    )
