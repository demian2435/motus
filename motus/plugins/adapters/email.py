"""Email output plugin for Motus (template, requires implementation)."""

from motus.adapter import OutputAdapter
from motus.registry import register_adapter


@register_adapter("email")
class EmailAdapter(OutputAdapter):
    async def execute(self, action, event) -> None:
        # Here you would integrate with an email service (SMTP, SendGrid, etc.)
        self.logger.info(
            f"EmailAdapter: would send email for action {action} and event {event}",
        )
