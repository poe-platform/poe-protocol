"""
LlamaIndex Bot.
"""
from __future__ import annotations

import logging
import os
from typing import AsyncIterable, Sequence

from fastapi.responses import JSONResponse
from langchain import LLMChain, OpenAI
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from llama_index import Document as LlamaDocument, IndexStructType
from llama_index.indices.base import BaseGPTIndex
from llama_index.indices.registry import INDEX_STRUCT_TYPE_TO_INDEX_CLASS
from llama_index.readers import SimpleDirectoryReader
from poe_api.types import AddDocumentsRequest, Document
from sse_starlette.sse import ServerSentEvent

from fastapi_poe.base import PoeHandler
from fastapi_poe.types import (
    QueryRequest,
    ReportFeedbackRequest,
    SettingsRequest,
    SettingsResponse,
)

LOAD_DATA = os.environ.get("LLAMA_LOAD_DATA", True)
DATA_DIR = os.environ.get("LLAMA_DATA_DIR", "data/")

INDEX_STRUCT_TYPE_STR = os.environ.get(
    "LLAMA_INDEX_TYPE", IndexStructType.SIMPLE_DICT.value
)
INDEX_JSON_PATH = os.environ.get("LLAMA_INDEX_JSON_PATH", "save/index.json")

EXTERNAL_VECTOR_STORE_INDEX_STRUCT_TYPES = [
    IndexStructType.DICT,
    IndexStructType.WEAVIATE,
    IndexStructType.PINECONE,
    IndexStructType.QDRANT,
    IndexStructType.CHROMA,
    IndexStructType.VECTOR_STORE,
]

SETTINGS = SettingsResponse(
    context_clear_window_secs=60 * 60, allow_user_context_clear=True
)

logger = logging.getLogger(__name__)


def _to_llama_documents(docs: Sequence[Document]) -> list[LlamaDocument]:
    return [LlamaDocument(text=doc.text, doc_id=doc.doc_id) for doc in docs]


def _create_or_load_index(
    index_type_str: str | None = None,
    index_json_path: str | None = None,
    index_type_to_index_cls: dict[str, type[BaseGPTIndex]] | None = None,
) -> BaseGPTIndex:
    """Create or load index from json path."""
    index_json_path = index_json_path or INDEX_JSON_PATH
    index_type_to_index_cls = (
        index_type_to_index_cls or INDEX_STRUCT_TYPE_TO_INDEX_CLASS
    )
    index_type_str = index_type_str or INDEX_STRUCT_TYPE_STR
    index_type = IndexStructType(index_type_str)

    if index_type not in index_type_to_index_cls:
        raise ValueError(f"Unknown index type: {index_type}")

    # TODO: support external vector store
    if index_type in EXTERNAL_VECTOR_STORE_INDEX_STRUCT_TYPES:
        raise ValueError("Please use vector store directly.")

    index_cls = index_type_to_index_cls[index_type]
    try:
        # Load index from disk
        index = index_cls.load_from_disk(index_json_path)
        logger.info(f"Loading index from {index_json_path}")
        return index
    except OSError:
        # Create empty index
        index = index_cls(nodes=[])
        logger.info("Creating new index")

        if LOAD_DATA:
            logger.info(f"Loading data from {DATA_DIR}")
            reader = SimpleDirectoryReader(input_dir=DATA_DIR)
            documents = reader.load_data()
            nodes = index.service_context.node_parser.get_nodes_from_documents(
                documents
            )
            index.insert_nodes(nodes)

        return index


def _get_chat_history(chat_history: list[tuple[str, str]]) -> str:
    buffer = ""
    for human_s, ai_s in chat_history:
        human = "Human: " + human_s
        ai = "Assistant: " + ai_s
        buffer += "\n" + "\n".join([human, ai])
    return buffer


class LlamaBotHandler(PoeHandler):
    def __init__(self) -> None:
        """Setup LlamaIndex."""
        self._chat_history = {}
        self._index = _create_or_load_index()

    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        """Return an async iterator of events to send to the user."""
        # Get chat history
        chat_history = self._chat_history.get(query.conversation_id)
        if chat_history is None:
            chat_history = []
            self._chat_history[query.conversation_id] = chat_history

        # Get last message
        last_message = query.query[-1].content

        # Generate standalone question from conversation context and last message
        question_gen_model = OpenAI(temperature=0)
        question_generator = LLMChain(
            llm=question_gen_model, prompt=CONDENSE_QUESTION_PROMPT
        )

        chat_history_str = _get_chat_history(chat_history)
        logger.debug(chat_history_str)
        new_question = question_generator.run(
            question=last_message, chat_history=chat_history_str
        )
        logger.info(f"Querying with: {new_question}")

        # Query with standalone question
        response = await self._index.aquery(
            new_question, streaming=True, similarity_top_k=3
        )
        full_response = ""
        for text in response.response_gen:
            full_response += text
            yield self.text_event(text)

        chat_history.append((last_message, full_response))

    async def on_feedback(self, feedback: ReportFeedbackRequest) -> None:
        """Called when we receive user feedback such as likes."""
        logger.info(
            f"User {feedback.user_id} gave feedback on {feedback.conversation_id}"
            f"message {feedback.message_id}: {feedback.feedback_type}"
        )

    async def get_settings(self, settings: SettingsRequest) -> SettingsResponse:
        """Return the settings for this bot."""
        return SETTINGS

    async def add_documents(self, request: AddDocumentsRequest) -> None:
        """Add documents."""
        llama_docs = _to_llama_documents(request.documents)
        nodes = self._index.service_context.node_parser.get_nodes_from_documents(
            llama_docs
        )
        self._index.insert_nodes(nodes)

    async def handle_add_documents(self, request: AddDocumentsRequest) -> JSONResponse:
        await self.add_documents(request)
        return JSONResponse({})

    def handle_shutdown(self) -> None:
        """Save index upon shutdown."""
        self._index.save_to_disk(INDEX_JSON_PATH)
