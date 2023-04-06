from __future__ import annotations

from typing import Any, Tuple, Union

from typing_extensions import Literal, NotRequired, TypeAlias, TypedDict

Identifier: TypeAlias = str
FeedbackType: TypeAlias = Literal["like", "dislike"]
ContentType: TypeAlias = Literal["text/markdown", "text/plain"]


class MessageFeedback(TypedDict):
    """Feedback for a message as used in the Poe protocol."""

    type: FeedbackType
    reason: NotRequired[str]


class ProtocolMessage(TypedDict):
    """A message as used in the Poe protocol."""

    role: Literal["system", "user", "bot"]
    content: str
    content_type: ContentType
    timestamp: int
    message_id: str
    feedback: list[MessageFeedback]


class BaseRequest(TypedDict):
    """Common data for all requests."""

    version: str
    type: Literal["query", "settings", "report_feedback", "report_error"]


class QueryRequest(BaseRequest):
    """Request parameters for a query request."""

    query: list[ProtocolMessage]
    user_id: Identifier
    conversation_id: Identifier
    message_id: Identifier


class MetaEvent(TypedDict):
    content_type: NotRequired[ContentType]
    linkify: NotRequired[bool]
    refetch_settings: NotRequired[bool]
    suggested_replies: NotRequired[bool]


class TextEvent(TypedDict):
    text: str


class ReplaceResponseEvent(TypedDict):
    text: str


class SuggestedReplyEvent(TypedDict):
    text: str


class ErrorEvent(TypedDict):
    allow_retry: NotRequired[bool]
    text: NotRequired[str]


class DoneEvent(TypedDict):
    pass  # no fields


Event: TypeAlias = Union[
    Tuple[Literal["meta"], MetaEvent],
    Tuple[Literal["text"], TextEvent],
    Tuple[Literal["replace_response"], ReplaceResponseEvent],
    Tuple[Literal["suggested_reply"], SuggestedReplyEvent],
    Tuple[Literal["error"], ErrorEvent],
    Tuple[Literal["done"], DoneEvent],
]


class SettingsRequest(BaseRequest):
    """Request parameters for a settings request."""


class ReportFeedbackRequest(BaseRequest):
    """Request parameters for a report_feedback request."""

    message_id: Identifier
    user_id: Identifier
    conversation_id: Identifier
    feedback_type: FeedbackType


class ReportErrorRequest(TypedDict):
    """Request parameters for a report_error request."""

    message: str
    metadata: dict[str, Any]


class SettingsResponse(TypedDict):
    context_clear_window_secs: NotRequired[int | None]
    allow_user_context_clear: NotRequired[bool]
