"""Dummy output plugin for Motus."""

from typing import Any

from motus.adapter import OutputAdapter
from motus.registry import register_adapter


@register_adapter("dummy")
class DummyAdapter(OutputAdapter):
    """Adapter that simply logs the action."""

    async def execute(
        self,
        action: dict[str, Any],
        event: dict[str, Any],
    ) -> None:
        """Log the action and event type."""
        self.logger.info(
            "DummyAdapter: triggered for event type '%s', action: %s",
            event.get("type"),
            action,
        )
