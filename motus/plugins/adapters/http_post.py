"""HTTP POST output plugin for Motus (template, requires implementation)."""

import aiohttp

from motus.adapter import OutputAdapter
from motus.registry import register_adapter


@register_adapter("http_post")
class HTTPPostAdapter(OutputAdapter):
    async def execute(self, action, event) -> None:
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
            self.logger.info(f"HTTPPostAdapter: POST to {url} status {resp.status}")
