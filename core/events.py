"""Internal event bus for pub/sub communication between components."""

import logging
from collections import defaultdict
from typing import Any, Callable

log = logging.getLogger("kaelstorm.events")


class EventBus:
    """Simple synchronous pub/sub event bus."""

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def on(self, event: str, handler: Callable) -> None:
        """Subscribe a handler to an event."""
        self._handlers[event].append(handler)

    def off(self, event: str, handler: Callable) -> None:
        """Unsubscribe a handler from an event."""
        try:
            self._handlers[event].remove(handler)
        except ValueError:
            pass

    def emit(self, event: str, data: Any = None) -> None:
        """Emit an event to all subscribed handlers."""
        for handler in self._handlers.get(event, []):
            try:
                handler(data)
            except Exception:
                log.exception("Error in handler for event '%s'", event)
