from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi_poe.types import (
    RawRequest,
    SettingsRequest,
    QueryRequest,
    ReportFeedbackRequest,
)
from typing import Callable, AsyncIterable

import json
import logging


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        try:
            body = await request.json()
            logger.info(f"Request body: {json.dumps(body)}")
        except:
            logger.error("Request body: Unable to parse JSON")

        response = await call_next(request)

        logger.debug(f"Response status: {response.status_code}")
        try:
            body = json.loads(response.body.decode())
            logger.debug(f"Response body: {json.dumps(body)}")
        except:
            logger.debug("Response body: Unable to parse JSON")

        return response


def exception_handler(request: Request, ex: HTTPException):
    logger.error(ex)


class PoeHandler:
    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        yield PoeHandler.text_event("hello")
        yield PoeHandler.done_event()

    async def get_settings(self, setting: SettingsRequest) -> JSONResponse:
        logger.info("Processing settings")
        return {}

    async def on_feedback(feedback_request: ReportFeedbackRequest) -> JSONResponse:
        logger.info("Processing feedbacks")
        pass

    @staticmethod
    def text_event(text: str) -> ServerSentEvent:
        return ServerSentEvent(data=json.dumps({"text": text}), event="text")

    @staticmethod
    def done_event() -> ServerSentEvent:
        return ServerSentEvent(event="done")


def run(handler: Callable):
    global logger
    logger = logging.getLogger("uvicorn.default")
    app = FastAPI()
    app.add_exception_handler(RequestValidationError, exception_handler)

    @app.post("/poe")
    async def run_inner(conversation_request: RawRequest):
        if conversation_request.type == "query":
            return EventSourceResponse(handler.get_response(conversation_request))
        elif conversation_request.type == "settings":
            return handler.get_settings(conversation_request)
        elif conversation_request.type == "report_feedback":
            return handler.on_feedback(conversation_request)
        else:
            raise HTTPException(status_code=501, detail="Unsupported request type")

    # Uncomment this line to print out request and response
    # app.add_middleware(LoggingMiddleware)
    logger.info("Starting")
    import uvicorn

    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["default"][
        "fmt"
    ] = "%(asctime)s - %(levelname)s - %(message)s"
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=log_config)


if __name__ == "__main__":
    run(PoeHandler())
