import argparse
import copy
import json
import logging
import os
import secrets
from typing import Any, AsyncIterable, Dict, Optional, Union

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi_poe.types import (
    ContentType,
    QueryRequest,
    ReportErrorRequest,
    ReportFeedbackRequest,
    SettingsRequest,
    SettingsResponse,
)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def set_body(self, request: Request):
        receive_ = await request._receive()

        async def receive():
            return receive_

        request._receive = receive

    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        try:
            # Per https://github.com/tiangolo/fastapi/issues/394#issuecomment-927272627
            # to avoid blocking.
            await self.set_body(request)
            body = await request.json()
            logger.debug(f"Request body: {json.dumps(body)}")
        except json.JSONDecodeError:
            logger.error("Request body: Unable to parse JSON")

        response = await call_next(request)

        logger.info(f"Response status: {response.status_code}")
        try:
            if hasattr(response, "body"):
                body = json.loads(response.body.decode())
                logger.debug(f"Response body: {json.dumps(body)}")
        except json.JSONDecodeError:
            logger.error("Response body: Unable to parse JSON")

        return response


def exception_handler(request: Request, ex: HTTPException):
    logger.error(ex)


http_bearer = HTTPBearer()


def auth_user(
    authorization: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> None:
    if auth_key is None:
        return
    if authorization.scheme != "Bearer" and authorization.credentials != auth_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )


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

    async def on_error(self, error_request: ReportErrorRequest) -> None:
        """Override this to record errors from the Poe server."""
        logger.error(f"Error from Poe server: {error_request}")

    # Helpers for generating responses

    @staticmethod
    def text_event(text: str) -> ServerSentEvent:
        return ServerSentEvent(data=json.dumps({"text": text}), event="text")

    @staticmethod
    def replace_response_event(text: str) -> ServerSentEvent:
        return ServerSentEvent(
            data=json.dumps({"text": text}), event="replace_response"
        )

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
        suggested_replies: bool = True,
    ) -> ServerSentEvent:
        return ServerSentEvent(
            data=json.dumps(
                {
                    "content_type": content_type,
                    "refetch_settings": refetch_settings,
                    "linkify": linkify,
                    "suggested_replies": suggested_replies,
                }
            ),
            event="meta",
        )

    @staticmethod
    def error_event(
        text: Optional[str] = None, *, allow_retry: bool = True
    ) -> ServerSentEvent:
        data: Dict[str, Union[bool, str]] = {"allow_retry": allow_retry}
        if text is not None:
            data["text"] = text
        return ServerSentEvent(data=json.dumps(data), event="error")

    # Internal handlers

    async def handle_report_feedback(
        self, feedback_request: ReportFeedbackRequest
    ) -> JSONResponse:
        await self.on_feedback(feedback_request)
        return JSONResponse({})

    async def handle_report_error(
        self, error_request: ReportErrorRequest
    ) -> JSONResponse:
        await self.on_error(error_request)
        return JSONResponse({})

    async def handle_settings(self, settings_request: SettingsRequest) -> JSONResponse:
        settings = await self.get_settings(settings_request)
        return JSONResponse(settings.dict())

    async def handle_query(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        try:
            async for event in self.get_response(query):
                yield event
        except Exception as e:
            logger.exception("Error responding to query")
            yield self.error_event(repr(e), allow_retry=False)
        yield self.done_event()


def generate_auth_key(api_key: str) -> str:
    if api_key:
        return api_key
    if os.environ.get("POE_API_KEY"):
        return os.environ["POE_API_KEY"]
    auth_key = secrets.token_urlsafe(32)
    print("Generated API key:")
    print(auth_key)
    print("Set this key in the 'API Key' field in the bot creation form.")
    return auth_key


def run(handler: PoeHandler, api_key: str = "") -> None:
    """
    Run a Poe bot server using FastAPI.

    :param handler: The bot handler.
    :param api_key: The Poe API key to use. If not provided, it will try to read
    the POE_API_KEY environment. If that is not set, the server will not require
    authentication.

    """
    parser = argparse.ArgumentParser("FastAPI sample Poe bot server")
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()
    port = args.port

    global logger
    logger = logging.getLogger("uvicorn.default")
    app = FastAPI()
    app.add_exception_handler(RequestValidationError, exception_handler)

    global auth_key
    auth_key = generate_auth_key(api_key)

    @app.get("/")
    async def index() -> Response:
        url = "https://poe.com/create_bot?api=1"
        return HTMLResponse(
            "<html><body><h1>FastAPI Poe bot server</h1><p>Congratulations! Your server"
            " is running. To connect it to Poe, create a bot at <a"
            f' href="{url}">{url}</a>.</p></body></html>'
        )

    @app.post("/")
    async def poe_post(request: Dict[str, Any], dict=Depends(auth_user)) -> Response:
        if request["type"] == "query":
            return EventSourceResponse(
                handler.handle_query(QueryRequest.parse_obj(request))
            )
        elif request["type"] == "settings":
            return await handler.handle_settings(SettingsRequest.parse_obj(request))
        elif request["type"] == "report_feedback":
            return await handler.handle_report_feedback(
                ReportFeedbackRequest.parse_obj(request)
            )
        elif request["type"] == "report_error":
            return await handler.handle_report_error(
                ReportErrorRequest.parse_obj(request)
            )
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
