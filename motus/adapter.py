"""Base class per Output Adapter."""

import abc
import logging
from typing import Any


class OutputAdapter(abc.ABC):
    """Base class for output adapters."""

    def __init__(self) -> None:
        """Initialize a logger for the adapter instance."""
        self.logger = logging.getLogger(self.__class__.__name__)

    @abc.abstractmethod
    async def execute(
        self,
        action: dict[str, Any],
        event: dict[str, Any],
    ) -> None:
        """Execute an action against the target system."""
