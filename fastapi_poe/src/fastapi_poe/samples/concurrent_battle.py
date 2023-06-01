"""

Sample bot that returns results from both Sage and Claude-Instant.

"""
from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import AsyncIterable, AsyncIterator, Sequence

from sse_starlette.sse import ServerSentEvent

from fastapi_poe import PoeBot, run
from fastapi_poe.client import BotMessage, MetaMessage, stream_request
from fastapi_poe.types import QueryRequest


async def advance_stream(
    label: str, gen: AsyncIterator[BotMessage]
) -> tuple[str, BotMessage | None]:
    try:
        return label, await gen.__anext__()
    except StopAsyncIteration:
        return label, None


async def combine_streams(
    streams: Sequence[tuple[str, AsyncIterator[BotMessage]]]
) -> AsyncIterator[tuple[str, BotMessage]]:
    active_streams = {label: gen for label, gen in streams}
    while active_streams:
        for coro in asyncio.as_completed(
            [advance_stream(label, gen) for label, gen in active_streams.items()]
        ):
            label, msg = await coro
            if msg is None:
                del active_streams[label]
            else:
                yield label, msg


class ConcurrentBattleBot(PoeBot):
    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        streams = [
            (bot, stream_request(query, bot, "key"))
            for bot in ("sage", "claude-instant")
        ]
        label_to_responses: dict[str, list[str]] = defaultdict(list)
        async for label, msg in combine_streams(streams):
            if isinstance(msg, MetaMessage):
                continue
            elif msg.is_suggested_reply:
                yield self.suggested_reply_event(msg.text)
                continue
            elif msg.is_replace_response:
                label_to_responses[label] = [msg.text]
            else:
                label_to_responses[label].append(msg.text)
            text = "\n\n".join(
                f"**{label.title()}** says:\n{''.join(chunks)}"
                for label, chunks in label_to_responses.items()
            )
            yield self.replace_response_event(text)


if __name__ == "__main__":
    run(ConcurrentBattleBot())
