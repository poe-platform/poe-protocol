"""

Demo bot: Altai the cat.

"""
from __future__ import annotations

from typing import AsyncIterator
from aiohttp import web

from aiohttp_poe import PoeHandler, run
from aiohttp_poe.types import (
    ReportFeedbackRequest,
    SettingsResponse,
    QueryRequest,
    Event,
)

SETTINGS: SettingsResponse = {
    "context_clear_window_secs": 60 * 60,
    "allow_user_context_clear": True,
}


class AltaiHandler(PoeHandler):
    async def get_response(
        self, query: QueryRequest, request: web.Request
    ) -> AsyncIterator[Event]:
        """Return an async iterator of events to send to the user."""
        last_message: str = query["query"][-1]["content"].lower()
        yield (
            "meta",
            {
                "content_type": "text/markdown",
                "linkify": True,
                "refetch_settings": False,
            },
        )
        if "cardboard" in last_message:
            yield ("text", {"text": "crunch "})
            yield ("text", {"text": "crunch"})
        elif (
            "kitchen" in last_message
            or "meal" in last_message
            or "food" in last_message
        ):
            yield ("text", {"text": "meow "})
            yield ("text", {"text": "meow"})
            yield ("suggested_reply", {"text": "Feed Altai"})
        else:
            yield ("text", {"text": "zzz"})

    async def on_feedback(self, feedback: ReportFeedbackRequest) -> None:
        """Called when we receive user feedback such as likes."""
        print(
            f"User {feedback['user_id']} gave feedback on {feedback['conversation_id']}"
            f"message {feedback['message_id']}: {feedback['feedback_type']}"
        )

    async def get_settings(self) -> SettingsResponse:
        """Return the settings for this bot."""
        return SETTINGS


if __name__ == "__main__":
    run(AltaiHandler())
