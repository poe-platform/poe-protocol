import json
from typing import Any, Callable, Awaitable
from aiohttp import web
from aiohttp_sse import sse_response, EventSourceResponse
import asyncio

SETTINGS = {
    "report_feedback": True,
    "context_clear_window_secs": 60 * 60,
    "allow_user_context_clear": True,
}


async def index(request: web.Request) -> web.Response:
    return web.Response(text="Altaibot")


class SSEResponse(EventSourceResponse):
    async def prepare(self, request: web.Request):
        """Prepare for streaming and send HTTP headers.
        :param request: regular aiohttp.web.Request.
        """
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


async def handle_query(request: web.Request, params: dict[str, Any]) -> web.Response:
    last_message: str = params["query"][-1]["content"].lower()
    async with sse_response(request, response_cls=SSEResponse) as resp:
        meta = {
            "content_type": "text/markdown",
            "linkify": True,
            "refetch_settings": False,
            "server_message_id": request.app["message_id"],
        }
        request.app["message_id"] += 1
        await resp.send(json.dumps(meta), event="meta")
        if "cardboard" in last_message:
            await resp.send(json.dumps({"text": "crunch "}), event="text")
            await resp.send(json.dumps({"text": "crunch"}), event="text")
        elif (
            "kitchen" in last_message
            or "meal" in last_message
            or "food" in last_message
        ):
            await resp.send(json.dumps({"text": "meow "}), event="text")
            await resp.send(json.dumps({"text": "meow"}), event="text")
            await resp.send(json.dumps({"text": "Feed Altai"}), event="suggested_reply")
        else:
            await resp.send(json.dumps({"text": "zzz"}), event="text")
        await resp.send("{}", event="done")


async def handle_settings(request: web.Request, params: dict[str, Any]) -> web.Response:
    return web.Response(text=json.dumps(SETTINGS), content_type="application/json")


async def handle_report_feedback(
    request: web.Request, params: dict[str, Any]
) -> web.Response:
    print(
        f"User {params['user']} gave feedback on {params['conversation']}"
        f"message {params.get('server_message_id')}: {params['feedback_type']}"
    )
    return web.Response(text="{}", content_type="application/json")


POE_REQUEST_HANDLERS: dict[
    str, Callable[[web.Request, dict[str, Any]], Awaitable[web.Response]]
] = {
    "query": handle_query,
    "settings": handle_settings,
    "report_feedback": handle_report_feedback,
}


async def poe(request: web.Request) -> web.Response:
    body = await request.json()
    request_type = body["type"]
    try:
        handler = POE_REQUEST_HANDLERS[request_type]
    except KeyError:
        return web.Response(
            status=501, text="Unsupported request type", reason="Not Implemented"
        )
    return await handler(request, body)


def run() -> None:
    app = web.Application()
    app.add_routes([web.get("/", index)])
    app.add_routes([web.get("/poe", poe)])
    app.add_routes([web.post("/poe", poe)])
    app["message_id"] = 1
    web.run_app(app)
