"""Tests for idempotency."""

from ideanance.core.resilience.idempotency import (
    IdempotencyStore,
    generate_idempotency_key,
    hash_content,
)


def test_idempotency_key_deterministic():
    k1 = generate_idempotency_key("ws-1", "agent-1", "hash-1")
    k2 = generate_idempotency_key("ws-1", "agent-1", "hash-1")
    assert k1 == k2
    assert len(k1) == 32


def test_idempotency_key_varies_with_input():
    k1 = generate_idempotency_key("ws-1", "agent-1", "hash-1")
    k2 = generate_idempotency_key("ws-1", "agent-1", "hash-2")
    assert k1 != k2


def test_hash_content_deterministic():
    h1 = hash_content({"a": 1, "b": 2})
    h2 = hash_content({"b": 2, "a": 1})  # Different key order
    assert h1 == h2  # sort_keys=True


def test_idempotency_store():
    store = IdempotencyStore()
    assert store.get("key1") is None

    store.set("key1", "value1")
    assert store.get("key1") == "value1"

    store.clear()
    assert store.get("key1") is None
