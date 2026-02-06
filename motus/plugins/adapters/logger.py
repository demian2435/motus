"""Logger output plugin for Motus (prints actions to stdout)."""

from typing import Any

from motus.adapter import OutputAdapter
from motus.registry import register_adapter


@register_adapter("logger")
class LoggerAdapter(OutputAdapter):
    """Write actions to the logger."""

    async def execute(
        self,
        action: dict[str, Any],
        event: dict[str, Any],
    ) -> None:
        """Log the provided message from the action payload."""
        _ = event  # not used by this adapter
        self.logger.info("LoggerAdapter: %s", action["message"])
