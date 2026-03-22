"""Tests for the in-process EventBus."""

from __future__ import annotations

import asyncio

from ideanance.core.events import Event, EventBus


async def test_publish_delivers_to_subscriber():
    bus = EventBus()
    queue = bus.subscribe("ws-1")

    event = Event(
        type="test.created",
        payload={"key": "value"},
        workspace_id="ws-1",
    )
    await bus.publish(event)

    received = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert received.type == "test.created"
    assert received.payload == {"key": "value"}


async def test_multiple_subscribers_receive_event():
    bus = EventBus()
    q1 = bus.subscribe("ws-1")
    q2 = bus.subscribe("ws-1")

    event = Event(
        type="test.fanout",
        payload={"n": 1},
        workspace_id="ws-1",
    )
    await bus.publish(event)

    r1 = await asyncio.wait_for(q1.get(), timeout=1.0)
    r2 = await asyncio.wait_for(q2.get(), timeout=1.0)
    assert r1.type == "test.fanout"
    assert r2.type == "test.fanout"


async def test_unsubscribe_stops_delivery():
    bus = EventBus()
    queue = bus.subscribe("ws-1")
    bus.unsubscribe("ws-1", queue)

    event = Event(
        type="test.after_unsub",
        payload={},
        workspace_id="ws-1",
    )
    await bus.publish(event)

    # Queue should be empty since we unsubscribed
    assert queue.empty()


async def test_workspace_isolation():
    bus = EventBus()
    q_ws1 = bus.subscribe("ws-1")
    q_ws2 = bus.subscribe("ws-2")

    event = Event(
        type="test.ws1_only",
        payload={"ws": "1"},
        workspace_id="ws-1",
    )
    await bus.publish(event)

    # ws-1 subscriber should receive the event
    r1 = await asyncio.wait_for(q_ws1.get(), timeout=1.0)
    assert r1.type == "test.ws1_only"

    # ws-2 subscriber should NOT receive the event
    assert q_ws2.empty()


async def test_event_has_unique_id():
    e1 = Event(type="a", payload={}, workspace_id="ws-1")
    e2 = Event(type="a", payload={}, workspace_id="ws-1")

    assert e1.id != e2.id
    assert len(e1.id) > 0
