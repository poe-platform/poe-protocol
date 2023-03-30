from typing import List, Optional

from pydantic import BaseModel
from typing_extensions import Literal, TypeAlias

Identifier: TypeAlias = str
FeedbackType: TypeAlias = Literal["like", "dislike"]
ContentType: TypeAlias = Literal["text/markdown", "text/plain"]


class MessageFeedback(BaseModel):
    """Feedback for a message as used in the Poe protocol."""

    type: FeedbackType
    reason: Optional[str]


class ProtocolMessage(BaseModel):
    """A message as used in the Poe protocol."""

    role: Literal["system", "user", "bot", "assistant"]
    content: str
    content_type: ContentType
    timestamp: int
    message_id: str
    message_type: Optional[str]
    feedback: List[MessageFeedback]


class RawRequest(BaseModel):
    """Raw request from Poe"""

    version: str
    type: str
    conversation_id: str
    user_id: str
    message_id: str
    query: List[ProtocolMessage]


class BaseRequest(BaseModel):
    """Common data for all requests."""

    version: str
    type: Literal["query", "settings", "report_feedback"]


class QueryRequest(BaseRequest):
    """Request parameters for a query request."""

    query: List[ProtocolMessage]
    user_id: Identifier
    conversation_id: Identifier
    message_id: Identifier


class SettingsRequest(BaseRequest):
    """Request parameters for a settings request."""


class ReportFeedbackRequest(BaseRequest):
    """Request parameters for a report_feedback request."""

    message_id: Identifier
    user_id: Identifier
    conversation_id: Identifier
    feedback_type: FeedbackType


class SettingsResponse(BaseModel):
    context_clear_window_secs: Optional[int] = None
    allow_user_context_clear: bool = True
