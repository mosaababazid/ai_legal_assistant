from __future__ import annotations

import logging
from typing import Any

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

from app.core.config import (
    DATA_INDEX_DIR,
    EMBEDDING_MODEL_NAME,
    LLM_MODEL_NAME,
    RAG_REQUEST_TIMEOUT_SECONDS,
    RAG_SIMILARITY_TOP_K,
)

logger = logging.getLogger(__name__)

_query_engine: Any | None = None


class IndexNotFoundError(RuntimeError):
    """Raised when the persisted RAG index is missing or incomplete."""


def _build_german_rag_prompt(problem_text: str) -> str:
    """
    Builds a strict RAG prompt that forces the assistant to only use retrieved law texts.

    Note: The prompt itself is in German because the assistant response must be German.
    """
    return (
        "Du bist ein juristischer Assistent in Deutschland.\n"
        "Die folgende Person hat ein konkretes rechtliches Problem und bittet um eine rechtliche Einschätzung.\n"
        "Antworte ausschließlich auf Deutsch.\n"
        "Nutze ausschließlich die bereitgestellten Gesetzestexte aus dem Index.\n"
        "Verwende keine eigenen Kenntnisse oder Vorwissen.\n"
        "Wenn die Antwort nicht aus dem bereitgestellten Gesetzestext abgeleitet werden kann, schreibe: "
        "'Nicht im Index vorhanden'.\n"
        "Verwende keine juristischen Fachbegriffe ohne Erklärung.\n"
        "Gib am Ende die verwendeten Paragraphen oder Gesetze an, aber ohne vollständige Zitate.\n\n"
        f"Problem:\n{problem_text}\n\n"
        "Was sollte die Person tun? Welche Rechte oder Möglichkeiten bestehen?"
    )


def _get_query_engine() -> Any:
    """
    Lazily loads the vector index once and reuses a configured query engine.

    This avoids re-reading the full index from disk on every request.
    """
    global _query_engine
    if _query_engine is not None:
        return _query_engine

    index_dir = DATA_INDEX_DIR
    if not index_dir.exists():
        raise IndexNotFoundError(f"Index directory not found: {index_dir}")

    # Basic sanity check for expected llama-index files
    expected_files = ["docstore.json", "index_store.json"]
    missing_files = [name for name in expected_files if not (index_dir / name).exists()]
    if missing_files:
        raise IndexNotFoundError(
            f"Index directory {index_dir} is missing required files: {', '.join(missing_files)}"
        )

    Settings.embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL_NAME)

    storage_context = StorageContext.from_defaults(persist_dir=str(index_dir))
    index = load_index_from_storage(storage_context)

    llm = Ollama(model=LLM_MODEL_NAME, request_timeout=RAG_REQUEST_TIMEOUT_SECONDS)

    _query_engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=RAG_SIMILARITY_TOP_K,
        response_mode="compact",
        node_postprocessors=[],
    )

    logger.info(
        "Initialized RAG query engine (index_dir=%s, llm=%s, embed=%s).",
        index_dir,
        LLM_MODEL_NAME,
        EMBEDDING_MODEL_NAME,
    )
    return _query_engine


def handle_legal_query_with_index(text: str) -> dict:
    """
    Executes a legal query against the persisted LlamaIndex vector store and returns:
    - recommendation: the generated German response
    - used_paragraphs: raw text from the retrieved source nodes
    """
    prompt = _build_german_rag_prompt(text)
    response = _get_query_engine().query(prompt)
    used_paragraphs = [node.node.text for node in response.source_nodes]

    return {"recommendation": str(response), "used_paragraphs": used_paragraphs}

