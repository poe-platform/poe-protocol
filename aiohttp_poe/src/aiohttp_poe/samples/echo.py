"""

Sample bot that echoes back messages.

"""
from __future__ import annotations

from typing import AsyncIterator

from aiohttp import web

from aiohttp_poe import PoeHandler, run
from aiohttp_poe.types import Event, QueryRequest


class EchoHandler(PoeHandler):
    async def get_response(
        self, query: QueryRequest, request: web.Request
    ) -> AsyncIterator[Event]:
        """Return an async iterator of events to send to the user."""
        last_message = query["query"][-1]["content"]
        yield self.text_event(last_message)


if __name__ == "__main__":
    run(EchoHandler())
