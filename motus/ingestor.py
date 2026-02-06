"""Base class for Event Ingestor."""

import abc
from collections.abc import Callable
from typing import Any


class EventIngestor(abc.ABC):
    """Base class for input ingestors."""

    def __init__(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Store the callback used to forward normalized events."""
        self.callback = callback

    @abc.abstractmethod
    async def start(self) -> None:
        """Start listening for events."""

    def normalize_event(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        """Normalize raw payloads into the standard event schema."""
        return {
            "type": raw_event.get("type"),
            "source": raw_event.get("source"),
            "metadata": raw_event.get("metadata", {}),
            "timestamp": raw_event.get("timestamp"),
        }
