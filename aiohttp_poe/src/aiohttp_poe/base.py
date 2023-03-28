from __future__ import annotations

from typing import AsyncIterator, Awaitable, Callable
from aiohttp import web
from aiohttp_sse import sse_response, EventSourceResponse
import asyncio
import json

from .types import Event, QueryRequest, ReportFeedbackRequest, SettingsResponse


# We need to override this to allow POST requests to use SSE
class _SSEResponse(EventSourceResponse):
    async def prepare(self, request: web.Request):
        if not self.prepared:
            writer = await web.StreamResponse.prepare(self, request)
            self._ping_task = asyncio.create_task(self._ping())
            # explicitly enabling chunked encoding, since content length
            # usually not known beforehand.
            self.enable_chunked_encoding()
            return writer
        else:
            # hackish way to check if connection alive
            # should be updated once we have proper API in aiohttp
            # https://github.com/aio-libs/aiohttp/issues/3105
            if request.protocol.transport is None:
                # request disconnected
                raise asyncio.CancelledError()


class PoeHandler:
    async def __call__(self, request: web.Request) -> web.Response:
        body = await request.json()
        request_type = body["type"]
        if request_type == "query":
            await self.__handle_query(body, request)
            # Apparently aiohttp's types don't work well with whatever aiohttp_sse
            # is doing to create a streaming response.
            return None  # type: ignore
        elif request_type == "settings":
            settings = await self.get_settings()
            return web.Response(
                text=json.dumps(settings), content_type="application/json"
            )
        elif request_type == "report_feedback":
            await self.on_feedback(body)
            return web.Response(text="{}", content_type="application/json")
        else:
            return web.Response(
                status=501, text="Unsupported request type", reason="Not Implemented"
            )

    async def __handle_query(self, query: QueryRequest, request: web.Request) -> None:
        async with sse_response(request, response_cls=_SSEResponse) as resp:
            async for event_type, data in self.get_response(query, request):
                await resp.send(json.dumps(data), event=event_type)
            await resp.send("{}", event="done")

    # Methods that may be overridden by subclasses

    def get_response(
        self, query: QueryRequest, request: web.Request
    ) -> AsyncIterator[Event]:
        """Return an async iterator of events to send to the user."""
        raise NotImplementedError

    async def on_feedback(self, feedback: ReportFeedbackRequest) -> None:
        """Called when we receive user feedback such as likes."""
        pass

    async def get_settings(self) -> SettingsResponse:
        """Return the settings for this bot."""
        return {}


async def index(request: web.Request) -> web.Response:
    return web.Response(text="Poe Demo")


def run(handler: Callable[[web.Request], Awaitable[web.Response | None]]) -> None:
    app = web.Application()
    app.add_routes([web.get("/", index)])
    app.add_routes([web.post("/", handler)])
    app["message_id"] = 1
    web.run_app(app)
