import json
from typing import Any, Callable, Awaitable
from aiohttp import web
from aiohttp_sse import sse_response

SETTINGS = {
    "report_feedback": True,
    "context_clear_window_secs": 60 * 60,
    "allow_user_context_clear": True,
}


async def index(request: web.Request) -> web.Response:
    return web.Response(text="Altaibot")


async def handle_query(request: web.Request, params: dict[str, Any]) -> web.Response:
    last_message: str = params["query"][-1]["content"].lower()
    async with sse_response(request) as resp:
        meta = {
            "content_type": "text/markdown",
            "linkify": True,
            "refetch_settings": False,
            "server_message_id": request.app["message_id"],
        }
        request.app["message_id"] += 1
        await resp.send(json.dumps(meta), type="meta")
        if "cardboard" in last_message:
            await resp.send(json.dumps({"text": "crunch "}), type="text")
            await resp.send(json.dumps({"text": "crunch"}), type="text")
        elif (
            "kitchen" in last_message
            or "meal" in last_message
            or "food" in last_message
        ):
            await resp.send(json.dumps({"text": "meow "}), type="text")
            await resp.send(json.dumps({"text": "meow"}), type="text")
            await resp.send(json.dumps({"text": "Feed Altai"}), type="followup")
        else:
            await resp.send(json.dumps({"text": "zzz"}), type="text")
        await resp.send("{}", type="done")


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
    return await handler(body)


def run() -> None:
    app = web.Application()
    app.add_routes([web.get("/", index)])
    app.add_routes([web.post("/poe", poe)])
    app["message_id"] = 1
    web.run_app(app)
