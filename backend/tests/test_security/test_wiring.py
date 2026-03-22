"""Tests for PLAN43 — security + observability wiring."""


import pytest

from core.events import EVENT_QUEUE_MAX_SIZE, Event, EventBus
from core.observability.context import (
    RequestContext,
    get_context,
    set_context,
)
from core.protocols import RateLimiterProtocol
from core.rate_limit import RateLimiter
from core.security.input_validation import (
    MAX_POLICY_YAML_SIZE,
    validate_content_size,
)
from core.security.secret_detection import has_secrets
from modules.governance.custom_framework import (
    CustomFrameworkService,
    YamlValidationError,
)

# --- EventBus global listener ---


async def test_event_bus_global_listener():
    bus = EventBus()
    received = []
    bus.add_global_listener(lambda e: received.append(e))

    await bus.publish(
        Event(
            type="test.event",
            workspace_id="ws-1",
            payload={"key": "value"},
        )
    )
    assert len(received) == 1
    assert received[0].type == "test.event"


async def test_event_bus_global_listener_receives_all_workspaces():
    bus = EventBus()
    received = []
    bus.add_global_listener(lambda e: received.append(e))

    await bus.publish(
        Event(type="e1", workspace_id="ws-1", payload={})
    )
    await bus.publish(
        Event(type="e2", workspace_id="ws-2", payload={})
    )
    assert len(received) == 2
    assert received[0].workspace_id == "ws-1"
    assert received[1].workspace_id == "ws-2"


async def test_event_bus_backpressure():
    bus = EventBus()
    queue = bus.subscribe("ws-1")

    # Fill queue to max
    for i in range(EVENT_QUEUE_MAX_SIZE):
        await bus.publish(
            Event(
                type="fill",
                workspace_id="ws-1",
                payload={"i": i},
            )
        )

    # One more should be silently dropped (not raise)
    await bus.publish(
        Event(
            type="overflow",
            workspace_id="ws-1",
            payload={},
        )
    )
    assert queue.qsize() == EVENT_QUEUE_MAX_SIZE


# --- RequestContext ---


def test_request_context_set_and_get():
    ctx = RequestContext(workspace_id="ws-test")
    set_context(ctx)
    retrieved = get_context()
    assert retrieved is not None
    assert retrieved.workspace_id == "ws-test"
    assert retrieved.request_id == ctx.request_id


# --- RateLimiter Protocol ---


def test_rate_limiter_implements_protocol():
    limiter = RateLimiter()
    assert isinstance(limiter, RateLimiterProtocol)


# --- YAML bomb defense ---


def test_yaml_bomb_depth_rejected():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")

    # Build valid but deeply nested YAML dict
    import yaml

    nested: dict = {"leaf": "value"}
    for i in range(15):
        nested = {f"level_{i}": nested}
    yaml_content = yaml.dump({"policy": nested})

    with pytest.raises(YamlValidationError, match="nesting"):
        svc.add_policy_from_yaml("fw", yaml_content)


def test_yaml_size_limit_rejected():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")

    # Build oversized YAML
    huge = "x" * (MAX_POLICY_YAML_SIZE + 1)
    with pytest.raises(YamlValidationError, match="byte limit"):
        svc.add_policy_from_yaml("fw", huge)


# --- Secret scanning ---


def test_secret_detection_catches_api_key():
    content = 'api_key: "sk-ant-abcdefghijklmnopqrstuvwxyz"'
    assert has_secrets(content) is True


def test_secret_detection_clean_content():
    content = "This is a normal policy with no secrets."
    assert has_secrets(content) is False


# --- Input validation ---


def test_validate_content_size_within_limit():
    assert validate_content_size("small", max_size=100) is True


def test_validate_content_size_exceeds_limit():
    assert validate_content_size("x" * 200, max_size=100) is False
