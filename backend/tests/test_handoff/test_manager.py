"""Tests for HandoffManager."""

from core.handoff.limits import MAX_HANDOFFS_PER_REQUEST
from core.handoff.manager import HandoffManager
from core.handoff.schema import HandoffRequest
from modules.agents import AGENT_IDS


def _request(
    source: str = AGENT_IDS["DESIGN_ADVISOR"],
    target: str = AGENT_IDS["EVAL_GENERATOR"],
    reason: str = "missing_required_input",
    trace_id: str = "trace-1",
) -> HandoffRequest:
    return HandoffRequest(
        trace_id=trace_id,
        source_agent=source,
        handoff_to=target,
        reason=reason,
        reason_detail="Need eval criteria",
    )


async def test_basic_handoff():
    mgr = HandoffManager()
    resp = await mgr.process_handoff(_request())
    assert resp.status == "resolved"
    assert resp.responding_agent == AGENT_IDS["EVAL_GENERATOR"]


async def test_handoff_limit_enforced():
    mgr = HandoffManager()
    # MAX_HANDOFFS_PER_REQUEST handoffs should work
    for i in range(MAX_HANDOFFS_PER_REQUEST):
        resp = await mgr.process_handoff(
            _request(trace_id="t1", source=f"agent_{i}")
        )
        assert resp.status == "resolved"

    # Next one should fail
    resp = await mgr.process_handoff(
        _request(trace_id="t1", source=f"agent_{MAX_HANDOFFS_PER_REQUEST}")
    )
    assert resp.status == "failed"
    assert "limit" in (resp.failure_reason or "").lower()


async def test_circular_detection():
    mgr = HandoffManager()
    req = _request()
    # Same source->target->reason twice is OK
    await mgr.process_handoff(req)
    await mgr.process_handoff(req)
    # Third triggers circular detection
    resp = await mgr.process_handoff(req)
    assert resp.status == "failed"
    assert "circular" in (resp.failure_reason or "").lower()


async def test_human_escalation():
    mgr = HandoffManager()
    resp = await mgr.process_handoff(
        _request(target="human")
    )
    assert resp.status == "escalated"
    assert resp.responding_agent == "human"


async def test_different_sources_independent():
    mgr = HandoffManager()
    for i in range(5):
        resp = await mgr.process_handoff(
            _request(
                trace_id=f"trace-{i}",
                source=f"agent_{i}",
                target=f"target_{i}",
            )
        )
        assert resp.status == "resolved"


async def test_reset_clears_state():
    mgr = HandoffManager()
    await mgr.process_handoff(_request())
    mgr.reset()
    assert len(mgr._history) == 0
    assert len(mgr._handoff_counts) == 0
