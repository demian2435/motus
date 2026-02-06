"""Base class per Output Adapter."""

import abc
import logging
from typing import Any


class OutputAdapter(abc.ABC):
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    @abc.abstractmethod
    async def execute(self, action: dict[str, Any], event: dict[str, Any]):
        pass
