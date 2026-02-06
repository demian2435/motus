"""Webhook input plugin for Motus."""

import asyncio

from aiohttp import web

from motus.ingestor import EventIngestor
from motus.registry import register_ingestor


@register_ingestor("webhook")
class WebhookIngestor(EventIngestor):
    def __init__(self, callback, host="0.0.0.0", port=8080) -> None:
        super().__init__(callback)
        self.host = host
        self.port = port
        self._app = web.Application()
        self._app.router.add_post("/event", self.handle_event)

    async def start(self) -> None:
        runner = web.AppRunner(self._app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        while True:
            await asyncio.sleep(3600)

    async def handle_event(self, request):
        data = await request.json()
        event = self.normalize_event(data)
        self.callback(event)
        return web.json_response({"status": "received"})
