"""Webhook input plugin for Motus."""

import asyncio
from collections.abc import Callable
from typing import Any

from aiohttp import web

from motus.ingestor import EventIngestor
from motus.registry import register_ingestor


@register_ingestor("webhook")
class WebhookIngestor(EventIngestor):
    """Expose an HTTP endpoint to ingest events."""

    def __init__(
        self,
        callback: Callable[[dict[str, Any]], None],
        host: str = "0.0.0.0",  # noqa: S104 - exposed by design for webhook
        port: int = 8080,
    ) -> None:
        """Create a webhook ingestor bound to the given host/port."""
        super().__init__(callback)
        self.host = host
        self.port = port
        self._app = web.Application()
        self._app.router.add_post("/event", self.handle_event)

    async def start(self) -> None:
        """Start the HTTP server and keep it running."""
        runner = web.AppRunner(self._app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        stop_event = asyncio.Event()
        await stop_event.wait()

    async def handle_event(self, request: web.Request) -> web.Response:
        """Process incoming JSON payloads and forward normalized events."""
        data = await request.json()
        event = self.normalize_event(data)
        self.callback(event)
        return web.json_response({"status": "received"})
