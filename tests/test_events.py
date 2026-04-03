"""Tests for internal event bus."""

from core.events import EventBus


def test_subscribe_and_emit():
    bus = EventBus()
    received = []
    bus.on("test_event", lambda data: received.append(data))
    bus.emit("test_event", {"key": "value"})
    assert received == [{"key": "value"}]


def test_multiple_subscribers():
    bus = EventBus()
    a, b = [], []
    bus.on("evt", lambda d: a.append(d))
    bus.on("evt", lambda d: b.append(d))
    bus.emit("evt", 42)
    assert a == [42]
    assert b == [42]


def test_emit_unknown_event_no_error():
    bus = EventBus()
    bus.emit("nonexistent", {})  # should not raise


def test_off_removes_handler():
    bus = EventBus()
    received = []
    handler = lambda d: received.append(d)
    bus.on("evt", handler)
    bus.off("evt", handler)
    bus.emit("evt", "ignored")
    assert received == []
