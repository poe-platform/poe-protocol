import json
from typing import Any, Callable, Awaitable, List
from collections import defaultdict
from aiohttp import web
from aiohttp_sse import sse_response, EventSourceResponse
import asyncio
import openai


SETTINGS = {
    "report_feedback": True,
    "context_clear_window_secs": 60 * 60,
    "allow_user_context_clear": True,
}

conversation_cache = defaultdict(
    lambda: [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
)

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


def process_message(user_statement: str) -> str:
    if "cardboard" in user_statement:
        return "crunch crunch\n\n"
    if "kitchen" in user_statement or "meal" in user_statement or "food" in user_statement:
        return "meow meow\n\n"
    return "zzz\n\n"

def process_message_with_gpt(message_history: List[dict[str, str]]) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history
    )
    bot_statement = response['choices'][0]['message']['content']
    return bot_statement


async def handle_query(request: web.Request, params: dict[str, Any]) -> web.Response:
    user_statement: str = params["query"][-1]["content"].lower()
    async with sse_response(request, response_cls=SSEResponse) as resp:
        meta = {
            "content_type": "text/markdown",
            "linkify": True,
            "refetch_settings": False,
            "server_message_id": request.app["message_id"],
        }
        request.app["message_id"] += 1
        await resp.send(json.dumps(meta), event="meta")

        conversation_cache[params['conversation']].append(
            {"role": "user", "content": user_statement},
        )

        for character in process_message(user_statement):
            await resp.send(json.dumps({"text": character}), event="text")

        if openai.api_key:
            message_history = conversation_cache[params['conversation']]
            bot_statement = process_message_with_gpt(message_history)
            await resp.send(json.dumps({"text": bot_statement}), event="text")

            conversation_cache[params['conversation']].append(
                {"role": "assistant", "content": bot_statement},
            )

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
