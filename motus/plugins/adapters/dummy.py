"""Dummy output plugin for Motus."""

from motus.adapter import OutputAdapter
from motus.registry import register_adapter


@register_adapter("dummy")
class DummyAdapter(OutputAdapter):
    async def execute(self, action, event) -> None:
        self.logger.info(
            f"DummyAdapter: triggered for event type '{event.get('type')}', action: {action}",
        )
