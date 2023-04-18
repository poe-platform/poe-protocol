import copy
import logging
import os
from typing import Any, Dict

import uvicorn.config
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from poe_api import llama_handler
from poe_api.types import AddDocumentsRequest
from poe_api.utils import LoggingMiddleware
from sse_starlette.sse import EventSourceResponse

from fastapi_poe.types import (
    QueryRequest,
    ReportErrorRequest,
    ReportFeedbackRequest,
    SettingsRequest,
)

global logger
logger = logging.getLogger("uvicorn.default")

http_bearer = HTTPBearer()
BEARER_TOKEN = os.environ.get("POE_API_KEY")
assert BEARER_TOKEN is not None


def exception_handler(request: Request, ex: HTTPException):
    del request
    logger.error(ex)


def auth_user(
    authorization: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> None:
    if authorization.scheme != "Bearer" or authorization.credentials != BEARER_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )


app = FastAPI()
app.add_exception_handler(RequestValidationError, exception_handler)

# Uncomment this line to print out request and response
app.add_middleware(LoggingMiddleware)
logger.info("Starting")

log_config = copy.deepcopy(uvicorn.config.LOGGING_CONFIG)
log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"


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
        return await handler.handle_report_error(ReportErrorRequest.parse_obj(request))
    else:
        raise HTTPException(status_code=501, detail="Unsupported request type")


@app.post("/add_document")
async def add_document(
    request_dict: Dict[str, Any], dict=Depends(auth_user)
) -> Response:
    request = AddDocumentsRequest.parse_obj(request_dict)
    return await handler.handle_add_documents(request)


@app.on_event("startup")
async def startup():
    global handler
    handler = llama_handler.LlamaBotHandler()


@app.on_event("shutdown")
def shutdown():
    handler.handle_shutdown()


def start():
    """
    Run a Poe bot server using FastAPI.

    :param handler: The bot handler.
    :param api_key: The Poe API key to use. If not provided, it will try to read
    the POE_API_KEY environment. If that is not set, the server will not require
    authentication.

    """
    uvicorn.run(
        "poe_api.server:app",
        host="0.0.0.0",
        port=8080,
        log_config=log_config,
        reload=True,
    )
