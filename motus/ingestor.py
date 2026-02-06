"""Base class for Event Ingestor."""

import abc
from collections.abc import Callable
from typing import Any


class EventIngestor(abc.ABC):
    def __init__(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self.callback = callback

    @abc.abstractmethod
    async def start(self):
        pass

    def normalize_event(self, raw_event: dict) -> dict:
        # Normalize according to standard schema
        return {
            "type": raw_event.get("type"),
            "source": raw_event.get("source"),
            "metadata": raw_event.get("metadata", {}),
            "timestamp": raw_event.get("timestamp"),
        }
