"""Email output plugin for Motus (template, requires implementation)."""

from typing import Any

from motus.adapter import OutputAdapter
from motus.registry import register_adapter


@register_adapter("email")
class EmailAdapter(OutputAdapter):
    """Example email adapter (stub)."""

    async def execute(
        self,
        action: dict[str, Any],
        event: dict[str, Any],
    ) -> None:
        """Pretend to send an email using the action payload."""
        # Here you would integrate with an email service (SMTP, SendGrid, etc.)
        self.logger.info(
            "EmailAdapter: would send email for action %s and event %s",
            action,
            event,
        )
