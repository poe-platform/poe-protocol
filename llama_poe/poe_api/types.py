from typing import List

from pydantic import BaseModel


class Document(BaseModel):
    doc_id: str
    text: str


class AddDocumentsRequest(BaseModel):
    """Request parameters for an add_documents request."""

    documents: List[Document]
