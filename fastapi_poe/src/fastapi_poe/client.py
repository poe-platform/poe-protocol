"""

Client for talking to other Poe bots through Poe's bot API.

"""
import asyncio
import contextlib
import json
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, cast

import httpx
import httpx_sse

from .types import ContentType, Identifier, QueryRequest, SettingsResponse

API_VERSION = "1.0"
MESSAGE_LENGTH_LIMIT = 10_000

IDENTIFIER_LENGTH = 32
MAX_EVENT_COUNT = 1000

ErrorHandler = Callable[[Exception, str], None]


class BotError(Exception):
    """Raised when there is an error communicating with the bot."""


class BotErrorNoRetry(BotError):
    """Subclass of BotError raised when we're not allowed to retry."""


class InvalidBotSettings(Exception):
    """Raised when a bot returns invalid settings."""


@dataclass
class BotMessage:
    """Representation of a (possibly partial) response from a bot."""

    text: str  # text of the message so far
    raw_response: object
    full_prompt: Optional[str]
    request_id: Optional[str] = None
    is_suggested_reply: bool = False

    # "is_replace_response" - represents if this text
    # should completely replace the previous bot text.
    is_replace_response: bool = False


@dataclass
class MetaMessage(BotMessage):
    """Communicate 'meta' events from API bots."""

    linkify: bool = True
    suggested_replies: bool = True
    content_type: ContentType = "text/markdown"


def _safe_ellipsis(obj: object, limit: int) -> str:
    if not isinstance(obj, str):
        obj = repr(obj)
    if len(obj) > limit:
        obj = obj[: limit - 3] + "..."
    return obj


@dataclass
class _BotContext:
    endpoint: str
    api_key: str = field(repr=False)
    session: httpx.AsyncClient = field(repr=False)
    on_error: Optional[ErrorHandler] = field(default=None, repr=False)

    @property
    def headers(self) -> Dict[str, str]:
        return {"Accept": "application/json", "Authorization": f"Bearer {self.api_key}"}

    async def report_error(
        self, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Report an error to the bot server."""
        if self.on_error is not None:
            long_message = (
                f"Protocol bot error: {message} with metadata {metadata} "
                f"for endpoint {self.endpoint}"
            )
            self.on_error(BotError(message), long_message)
        await self.session.post(
            self.endpoint,
            headers=self.headers,
            json={
                "version": API_VERSION,
                "type": "report_error",
                "message": message,
                "metadata": metadata or {},
            },
        )

    async def report_feedback(
        self,
        message_id: Identifier,
        user_id: Identifier,
        conversation_id: Identifier,
        feedback_type: str,
    ) -> None:
        """Report message feedback to the bot server."""
        await self.session.post(
            self.endpoint,
            headers=self.headers,
            json={
                "version": API_VERSION,
                "type": "report_feedback",
                "message_id": message_id,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "feedback_type": feedback_type,
            },
        )

    async def fetch_settings(self) -> SettingsResponse:
        """Fetches settings from a Poe API Bot Endpoint."""
        resp = await self.session.post(
            self.endpoint,
            headers=self.headers,
            json={"version": API_VERSION, "type": "settings"},
        )
        return resp.json()

    async def perform_query_request(
        self, request: QueryRequest
    ) -> AsyncGenerator[BotMessage, None]:
        chunks: List[str] = []
        message_id = request.message_id
        event_count = 0
        error_reported = False
        async with httpx_sse.aconnect_sse(
            self.session,
            "POST",
            self.endpoint,
            headers=self.headers,
            json=request.dict(),
        ) as event_source:
            async for event in event_source.aiter_sse():
                event_count += 1
                if event_count > MAX_EVENT_COUNT:
                    await self.report_error(
                        "Bot returned too many events", {"message_id": message_id}
                    )
                    raise BotErrorNoRetry("Bot returned too many events")
                if event.event == "done":
                    # Don't send a report if we already told the bot about some other mistake.
                    if not chunks and not error_reported:
                        await self.report_error(
                            "Bot returned no text in response",
                            {"message_id": message_id},
                        )
                    return
                elif event.event == "text":
                    text = await self._get_single_json_field(
                        event.data, "text", message_id
                    )
                elif event.event == "replace_response":
                    text = await self._get_single_json_field(
                        event.data, "replace_response", message_id
                    )
                    chunks.clear()
                elif event.event == "suggested_reply":
                    text = await self._get_single_json_field(
                        event.data, "suggested_reply", message_id
                    )
                    yield BotMessage(
                        text=text,
                        raw_response={"type": event.event, "text": event.data},
                        full_prompt=repr(request),
                        is_suggested_reply=True,
                    )
                    continue
                elif event.event == "meta":
                    if event_count != 1:
                        # spec says a meta event that is not the first event is ignored
                        continue
                    data = await self._load_json_dict(event.data, "meta", message_id)
                    linkify = data.get("linkify", False)
                    if not isinstance(linkify, bool):
                        await self.report_error(
                            "Invalid linkify value in 'meta' event",
                            {"message_id": message_id, "linkify": linkify},
                        )
                        error_reported = True
                        continue
                    send_suggested_replies = data.get("suggested_replies", False)
                    if not isinstance(send_suggested_replies, bool):
                        await self.report_error(
                            "Invalid suggested_replies value in 'meta' event",
                            {
                                "message_id": message_id,
                                "suggested_replies": send_suggested_replies,
                            },
                        )
                        error_reported = True
                        continue
                    content_type = data.get("content_type", "text/markdown")
                    if not isinstance(content_type, str):
                        await self.report_error(
                            "Invalid content_type value in 'meta' event",
                            {"message_id": message_id, "content_type": content_type},
                        )
                        error_reported = True
                        continue
                    yield MetaMessage(
                        "",
                        data,
                        full_prompt=repr(request),
                        linkify=linkify,
                        suggested_replies=send_suggested_replies,
                        content_type=cast(ContentType, content_type),
                    )
                    continue
                elif event.event == "error":
                    data = await self._load_json_dict(event.data, "error", message_id)
                    if data.get("allow_retry", True):
                        raise BotError(event.data)
                    else:
                        raise BotErrorNoRetry(event.data)
                elif event.event == "ping":
                    # Not formally part of the spec, but FastAPI sends this; let's ignore it
                    # instead of sending error reports.
                    continue
                else:
                    # Truncate the type and message in case it's huge.
                    await self.report_error(
                        f"Unknown event type: {_safe_ellipsis(event.event, 100)}",
                        {
                            "event_data": _safe_ellipsis(event.data, 500),
                            "message_id": message_id,
                        },
                    )
                    error_reported = True
                    continue
                chunks.append(text)
                total_length = sum(len(chunk) for chunk in chunks)
                if total_length > MESSAGE_LENGTH_LIMIT:
                    await self.report_error(
                        "Bot returned too much text",
                        {"message_id": message_id, "response_length": total_length},
                    )
                    raise BotErrorNoRetry("Bot returned too much text")
                yield BotMessage(
                    text=text,
                    raw_response={"type": event.event, "text": event.data},
                    full_prompt=repr(request),
                    is_replace_response=(event.event == "replace_response"),
                )
        await self.report_error(
            "Bot exited without sending 'done' event", {"message_id": message_id}
        )

    async def _get_single_json_field(
        self, data: str, context: str, message_id: Identifier, field: str = "text"
    ) -> str:
        data_dict = await self._load_json_dict(data, context, message_id)
        text = data_dict[field]
        if not isinstance(text, str):
            await self.report_error(
                f"Expected string in '{field}' field for '{context}' event",
                {"data": data_dict, "message_id": message_id},
            )
            raise BotErrorNoRetry(f"Expected string in '{context}' event")
        return text

    async def _load_json_dict(
        self, data: str, context: str, message_id: Identifier
    ) -> Dict[str, object]:
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            await self.report_error(
                f"Invalid JSON in {context!r} event",
                {"data": data, "message_id": message_id},
            )
            # If they are returning invalid JSON, retrying immediately probably won't help
            raise BotErrorNoRetry(f"Invalid JSON in {context!r} event")
        if not isinstance(parsed, dict):
            await self.report_error(
                f"Expected JSON dict in {context!r} event",
                {"data": data, "message_id": message_id},
            )
            raise BotError(f"Expected JSON dict in {context!r} event")
        return cast(Dict[str, object], parsed)


def _default_error_handler(e: Exception, msg: str) -> None:
    print("Error in Poe API Bot:", msg, e)


async def stream_request(
    request: QueryRequest,
    bot_name: str,
    api_key: str,
    *,
    session: Optional[httpx.AsyncClient] = None,
    on_error: ErrorHandler = _default_error_handler,
    num_tries: int = 2,
    retry_sleep_time: float = 0.5,
    base_url: str = "https://api.poe.com/bot/",
) -> AsyncGenerator[BotMessage, None]:
    """Streams BotMessages from an API bot."""
    async with contextlib.AsyncExitStack() as stack:
        if session is None:
            session = await stack.enter_async_context(httpx.AsyncClient())
        url = f"{base_url}{bot_name}"
        ctx = _BotContext(
            endpoint=url, api_key=api_key, session=session, on_error=on_error
        )
        got_response = False
        for i in range(num_tries):
            try:
                async for message in ctx.perform_query_request(request):
                    got_response = True
                    yield message
                break
            except BotErrorNoRetry:
                raise
            except Exception as e:
                on_error(e, f"Bot request to {bot_name} failed on try {i}")
                if got_response or i == num_tries - 1:
                    raise BotError(f"Error communicating with bot {bot_name}") from e
                await asyncio.sleep(retry_sleep_time)


async def get_final_response(request: QueryRequest, bot_name: str, api_key: str) -> str:
    """Gets the final response from an API bot."""
    chunks: List[str] = []
    async for message in stream_request(request, bot_name, api_key):
        if isinstance(message, MetaMessage):
            continue
        if message.is_suggested_reply:
            continue
        if message.is_replace_response:
            chunks.clear()
        chunks.append(message.text)
    if not chunks:
        raise BotError(f"Bot {bot_name} sent no response")
    return "".join(chunks)
