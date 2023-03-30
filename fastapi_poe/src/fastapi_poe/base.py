from __future__ import annotations

import argparse
import copy
import json
import logging
from typing import AsyncIterable

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi_poe.types import (
    ContentType,
    QueryRequest,
    RawRequest,
    ReportFeedbackRequest,
    SettingsRequest,
    SettingsResponse,
)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        try:
            body = await request.json()
            logger.info(f"Request body: {json.dumps(body)}")
        except json.JSONDecodeError:
            logger.error("Request body: Unable to parse JSON")

        response = await call_next(request)

        logger.debug(f"Response status: {response.status_code}")
        try:
            if hasattr(response, "body"):
                body = json.loads(response.body.decode())
                logger.debug(f"Response body: {json.dumps(body)}")
        except json.JSONDecodeError:
            logger.debug("Response body: Unable to parse JSON")

        return response


def exception_handler(request: Request, ex: HTTPException):
    logger.error(ex)


class PoeHandler:
    # Override these for your bot

    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        """Override this to return a response to user queries."""
        yield self.text_event("hello")

    async def get_settings(self, setting: SettingsRequest) -> SettingsResponse:
        """Override this to return non-standard settings."""
        return SettingsResponse()

    async def on_feedback(self, feedback_request: ReportFeedbackRequest) -> None:
        """Override this to record feedback from the user."""
        pass

    # Helpers for generating responses

    @staticmethod
    def text_event(text: str) -> ServerSentEvent:
        return ServerSentEvent(data=json.dumps({"text": text}), event="text")

    @staticmethod
    def done_event() -> ServerSentEvent:
        return ServerSentEvent(data="{}", event="done")

    @staticmethod
    def suggested_reply_event(text: str) -> ServerSentEvent:
        return ServerSentEvent(data=json.dumps({"text": text}), event="suggested_reply")

    @staticmethod
    def meta_event(
        *,
        content_type: ContentType = "text/markdown",
        refetch_settings: bool = False,
        linkify: bool = True,
    ) -> ServerSentEvent:
        return ServerSentEvent(
            data=json.dumps(
                {
                    "content_type": content_type,
                    "refetch_settings": refetch_settings,
                    "linkify": linkify,
                }
            ),
            event="meta",
        )

    @staticmethod
    def error_event(
        text: str | None = None, *, allow_retry: bool = True
    ) -> ServerSentEvent:
        data: dict[str, bool | str] = {"allow_retry": allow_retry}
        if text is not None:
            data["text"] = text
        return ServerSentEvent(data=json.dumps(data), event="error")

    # Internal handlers

    async def handle_report_feedback(
        self, feedback_request: ReportFeedbackRequest
    ) -> JSONResponse:
        await self.on_feedback(feedback_request)
        return JSONResponse({})

    async def handle_settings(self, settings_request: SettingsRequest) -> JSONResponse:
        settings = await self.get_settings(settings_request)
        return JSONResponse(settings.dict())

    async def handle_query(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        async for event in self.get_response(query):
            yield event
        yield self.done_event()


def run(handler: PoeHandler) -> None:
    parser = argparse.ArgumentParser("FastAPI sample Poe bot server")
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()
    port = args.port

    global logger
    logger = logging.getLogger("uvicorn.default")
    app = FastAPI()
    app.add_exception_handler(RequestValidationError, exception_handler)

    @app.post("/")
    async def run_inner(conversation_request: RawRequest):
        if conversation_request.type == "query":
            return EventSourceResponse(handler.handle_query(conversation_request))
        elif conversation_request.type == "settings":
            return handler.handle_settings(conversation_request)
        elif conversation_request.type == "report_feedback":
            return handler.handle_report_feedback(conversation_request)
        else:
            raise HTTPException(status_code=501, detail="Unsupported request type")

    # Uncomment this line to print out request and response
    # app.add_middleware(LoggingMiddleware)
    logger.info("Starting")
    import uvicorn.config

    log_config = copy.deepcopy(uvicorn.config.LOGGING_CONFIG)
    log_config["formatters"]["default"][
        "fmt"
    ] = "%(asctime)s - %(levelname)s - %(message)s"
    uvicorn.run(app, host="0.0.0.0", port=port, log_config=log_config)


if __name__ == "__main__":
    run(PoeHandler())
