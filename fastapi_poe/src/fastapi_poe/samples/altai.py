"""

Demo bot: Altai the cat.

"""
from __future__ import annotations

from typing import AsyncIterable

from fastapi.responses import JSONResponse
from sse_starlette.sse import ServerSentEvent
from fastapi_poe import PoeHandler, run
from fastapi_poe.types import ReportFeedbackRequest, QueryRequest

SETTINGS = {"context_clear_window_secs": 60 * 60, "allow_user_context_clear": True}


class AltaiHandler(PoeHandler):
    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        """Return an async iterator of events to send to the user."""
        last_message = query.query[-1].content.lower()
        yield self.meta_event(
            content_type="text/markdown", linkify=True, refetch_settings=False
        )
        if "cardboard" in last_message:
            yield self.text_event("crunch ")
            yield self.text_event("crunch")
        elif (
            "kitchen" in last_message
            or "meal" in last_message
            or "food" in last_message
        ):
            yield self.text_event("meow ")
            yield self.text_event("meow")
            yield self.suggested_reply_event("feed altai")
        else:
            yield self.text_event("zzz")
        yield self.done_event()

    async def on_feedback(self, feedback: ReportFeedbackRequest) -> None:
        """Called when we receive user feedback such as likes."""
        print(
            f"User {feedback.user_id} gave feedback on {feedback.conversation_id}"
            f"message {feedback.message_id}: {feedback.feedback_type}"
        )

    async def get_settings(self) -> JSONResponse:
        """Return the settings for this bot."""
        return JSONResponse(SETTINGS)


if __name__ == "__main__":
    run(AltaiHandler())
