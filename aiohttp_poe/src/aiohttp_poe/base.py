from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import AsyncIterator, Awaitable, Callable

from aiohttp import web
from aiohttp_sse import EventSourceResponse, sse_response

from .types import (
    ContentType,
    ErrorEvent,
    Event,
    QueryRequest,
    ReportErrorRequest,
    ReportFeedbackRequest,
    SettingsResponse,
)


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


async def authenticate(request: web.Request, token: str) -> bool:
    if auth_key is not None and token != auth_key:
        return False
    return True


@web.middleware
async def auth_middleware(request: web.Request, handler):
    auth_header = request.headers.get("Authorization")
    if auth_header:
        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() == "bearer":
            is_authenticated = await authenticate(request, token)
            if is_authenticated:
                return await handler(request)
    return web.HTTPUnauthorized(headers={"WWW-Authenticate": "Bearer"})


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
        elif request_type == "report_error":
            await self.on_error(body)
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

    @staticmethod
    def text_event(text: str) -> Event:
        return ("text", {"text": text})

    @staticmethod
    def replace_response_event(text: str) -> Event:
        return ("replace_response", {"text": text})

    @staticmethod
    def suggested_reply_event(text: str) -> Event:
        return ("suggested_reply", {"text": text})

    @staticmethod
    def meta_event(
        *,
        content_type: ContentType = "text/markdown",
        refetch_settings: bool = False,
        linkify: bool = True,
        suggested_replies: bool = True,
    ) -> Event:
        return (
            "meta",
            {
                "content_type": content_type,
                "refetch_settings": refetch_settings,
                "linkify": linkify,
                "suggested_replies": suggested_replies,
            },
        )

    @staticmethod
    def error_event(text: str | None = None, *, allow_retry: bool = True) -> Event:
        data: ErrorEvent = {"allow_retry": allow_retry}
        if text is not None:
            data["text"] = text
        return ("error", data)

    # Methods that may be overridden by subclasses

    def get_response(
        self, query: QueryRequest, request: web.Request
    ) -> AsyncIterator[Event]:
        """Return an async iterator of events to send to the user."""
        raise NotImplementedError

    async def on_error(self, error: ReportErrorRequest) -> None:
        """Called when the Poe server reports an error."""
        print("Received error:", error)

    async def on_feedback(self, feedback: ReportFeedbackRequest) -> None:
        """Called when we receive user feedback such as likes."""
        pass

    async def get_settings(self) -> SettingsResponse:
        """Return the settings for this bot."""
        return {}


async def index(request: web.Request) -> web.Response:
    url = "https://poe.com/create_bot?api=1"
    return web.Response(
        text="<html><body><h1>aiohttp Poe bot server</h1><p>Congratulations! Your server"
        " is running. To connect it to Poe, create a bot at <a"
        f' href="{url}">{url}</a>.</p></body></html>',
        content_type="text/html",
    )


def run(
    handler: Callable[[web.Request], Awaitable[web.Response]], api_key: str = ""
) -> None:
    parser = argparse.ArgumentParser("aiohttp sample Poe bot server")
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    global auth_key
    auth_key = api_key if api_key else os.environ.get("POE_API_KEY")

    app = web.Application(middlewares=[auth_middleware])
    app.add_routes([web.get("/", index)])
    app.add_routes([web.post("/", handler)])
    web.run_app(app, port=args.port)
