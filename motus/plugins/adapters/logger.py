"""Logger output plugin for Motus (prints actions to stdout)."""

from motus.adapter import OutputAdapter
from motus.registry import register_adapter


@register_adapter("logger")
class LoggerAdapter(OutputAdapter):
    async def execute(self, action, event) -> None:
        self.logger.info(f"LoggerAdapter: {action['message']}")
