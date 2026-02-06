"""Example custom adapter that echoes actions.

Run with --plugins-root examples/plugins to load this adapter.
"""

from typing import Any

from motus.adapter import OutputAdapter
from motus.registry import register_adapter


@register_adapter("echo")
class EchoAdapter(OutputAdapter):
    """Echo the provided message to the logger."""

    async def execute(self, action: dict[str, Any], event: dict[str, Any]) -> None:
        """Log the message from the action payload."""
        message = action.get("message") or "(no message)"
        _ = event  # event unused
        self.logger.info("EchoAdapter: %s", message)
