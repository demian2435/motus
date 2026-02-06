"""HTTP POST output plugin for Motus (template, requires implementation)."""

from typing import Any

import aiohttp

from motus.adapter import OutputAdapter
from motus.registry import register_adapter


@register_adapter("http_post")
class HTTPPostAdapter(OutputAdapter):
    """Send actions via HTTP POST."""

    async def execute(
        self,
        action: dict[str, Any],
        event: dict[str, Any],
    ) -> None:
        """Send the action + event payload to the configured URL."""
        url = action.get("url")
        if not url:
            self.logger.warning("HTTPPostAdapter: No URL specified in action")
            return
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                url,
                json={"action": action, "event": event},
            ) as resp,
        ):
            self.logger.info(
                "HTTPPostAdapter: POST to %s status %s",
                url,
                resp.status,
            )
