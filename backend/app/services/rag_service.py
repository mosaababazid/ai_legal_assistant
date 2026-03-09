# RAG over persisted index. Embedding and LLM come from config; you can choose
# models that suit you (see app/core/config.py). Uses hybrid retrieval + strict QA prompt.
from __future__ import annotations

import logging
from typing import Any

from llama_index.core import (
    PromptTemplate,
    Settings,
    StorageContext,
    get_response_synthesizer,
    load_index_from_storage,
)
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
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

STRICT_QA_PROMPT = PromptTemplate(
    "Du bist ein präziser deutscher Rechtsassistent. Deine Aufgabe ist es, dem Nutzer basierend auf seinem Brief und dem Gesetzestext klare Anweisungen zu geben.\n\n"
    "STRIKTE REGELN:\n"
    "1. Nutze AUSSCHLIESSLICH den angegebenen Kontext. Erfinde absolut nichts hinzu!\n"
    "2. Zahlen, Beträge (z.B. Euro) und Daten (z.B. Fristen) müssen EXAKT aus dem Brief übernommen werden.\n"
    "3. Sprich den Leser direkt mit 'Sie' an (z.B. 'Sie müssen...', 'Ihre Frist ist...').\n"
    "4. Keine Meta-Sätze! Beginne NICHT mit 'Dieser Brief besagt...' oder 'In dem Schreiben geht es um...'. Antworte sofort mit den Fakten.\n"
    "5. Fasse dich extrem kurz: Maximal 2 bis 4 einfache Sätze auf Deutsch. Keine langen Gesetzestexte kopieren.\n"
    "6. Wenn der Kontext nicht zum Brief passt, antworte NUR mit: 'Keine relevanten Paragraphen gefunden.'\n\n"
    "Gesetzlicher Kontext:\n{context_str}\n\n"
    "Brief/Text des Nutzers:\n{query_str}\n\n"
    "Klare und direkte Antwort (nur auf Deutsch):"
)

class IndexNotFoundError(RuntimeError):
    """Raised when index_store is missing or missing docstore.json/index_store.json."""


class _HybridRetriever(BaseRetriever):
    """Combines vector and BM25 retrievers with weighted scores (no EnsembleRetriever dependency)."""

    def __init__(
        self,
        vector_retriever: BaseRetriever,
        bm25_retriever: BaseRetriever,
        weights: tuple[float, float] = (0.5, 0.5),
        top_k: int = 5,
    ):
        super().__init__()
        self._vector = vector_retriever
        self._bm25 = bm25_retriever
        self._w_vec, self._w_bm25 = weights
        self._top_k = top_k

    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        from llama_index.core.async_utils import run_async_tasks

        vec_nodes = self._vector.retrieve(query_bundle)
        bm25_nodes = self._bm25.retrieve(query_bundle)
        seen: dict[str, NodeWithScore] = {}
        for n in vec_nodes:
            key = n.node.node_id
            score = (n.score or 0.0) * self._w_vec
            seen[key] = NodeWithScore(node=n.node, score=score)
        for n in bm25_nodes:
            key = n.node.node_id
            score = (n.score or 0.0) * self._w_bm25
            if key in seen:
                seen[key].score = (seen[key].score or 0) + score
            else:
                seen[key] = NodeWithScore(node=n.node, score=score)
        sorted_nodes = sorted(seen.values(), key=lambda x: x.score or 0.0, reverse=True)
        return sorted_nodes[: self._top_k]


def _get_query_engine() -> Any:
    """Load index once; build hybrid retriever (vector + BM25) and query engine with strict prompt."""
    global _query_engine
    if _query_engine is not None:
        return _query_engine

    index_dir = DATA_INDEX_DIR
    if not index_dir.exists():
        raise IndexNotFoundError(f"Index directory not found: {index_dir}")

    expected_files = ["docstore.json", "index_store.json"]
    missing_files = [name for name in expected_files if not (index_dir / name).exists()]
    if missing_files:
        raise IndexNotFoundError(
            f"Index directory {index_dir} is missing required files: {', '.join(missing_files)}"
        )

    Settings.embed_model = HuggingFaceEmbedding(
        model_name=EMBEDDING_MODEL_NAME,
    )

    storage_context = StorageContext.from_defaults(persist_dir=str(index_dir))
    index = load_index_from_storage(storage_context)

    vector_retriever = index.as_retriever(similarity_top_k=RAG_SIMILARITY_TOP_K)

    retriever = vector_retriever
    try:
        from llama_index.retrievers.bm25 import BM25Retriever

        docstore = storage_context.docstore
        node_ids = list(docstore.docs.keys()) if hasattr(docstore, "docs") else []
        if not node_ids:
            node_ids = getattr(index.index_struct, "node_ids", None) or []
        if node_ids:
            nodes = [docstore.get_node(nid) for nid in node_ids]
            nodes = [n for n in nodes if n is not None]
            if nodes:
                bm25_retriever = BM25Retriever.from_defaults(
                    nodes=nodes,
                    similarity_top_k=RAG_SIMILARITY_TOP_K,
                )
                retriever = _HybridRetriever(
                    vector_retriever,
                    bm25_retriever,
                    weights=(0.5, 0.5),
                    top_k=RAG_SIMILARITY_TOP_K,
                )
                logger.info("RAG using hybrid retriever (vector + BM25).")
    except Exception as e:
        logger.warning("BM25/hybrid not available, using vector only: %s", e)

    llm = Ollama(model=LLM_MODEL_NAME, request_timeout=RAG_REQUEST_TIMEOUT_SECONDS)
    response_synthesizer = get_response_synthesizer(
        llm=llm,
        text_qa_template=STRICT_QA_PROMPT,
    )
    _query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
    )

    logger.info(
        "Initialized RAG query engine (index_dir=%s, llm=%s, embed=%s).",
        index_dir,
        LLM_MODEL_NAME,
        EMBEDDING_MODEL_NAME,
    )
    return _query_engine


def handle_legal_query_with_index(text: str) -> dict:
    """Query index with problem text; return recommendation (DE) + used_paragraphs (source chunks)."""
    response = _get_query_engine().query(text)
    recommendation = str(response) if response is not None else ""
    nodes = getattr(response, "source_nodes", None) or []
    used_paragraphs = []
    for node in nodes:
        try:
            if getattr(node, "node", None) is not None:
                used_paragraphs.append(node.node.text)
        except Exception:
            pass

    return {"recommendation": recommendation, "used_paragraphs": used_paragraphs}
