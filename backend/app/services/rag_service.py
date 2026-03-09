from __future__ import annotations

import logging
import os
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
from llama_index.llms.groq import Groq

from app.core.config import (
    DATA_INDEX_DIR,
    EMBEDDING_MODEL_NAME,
    LLM_MODEL_NAME,
    RAG_REQUEST_TIMEOUT_SECONDS,
    RAG_SIMILARITY_TOP_K,
)

logger = logging.getLogger(__name__)

_query_engine: Any | None = None  # singleton; built once on first legal_advice request

LEGAL_CONSULTANT_PROMPT = PromptTemplate(
    "Du bist ein Rechtsberater. Du bekommst einen BRIEF und KONTEXT mit Gesetzestexten.\n\n"
    "PFLICHT: Die erste Zeile der Nutzeranfrage legt die AUSGABESPACHE fest (Deutsch oder Arabisch). "
    "Du MUSST die GESAMTE Beratung in genau dieser Sprache schreiben. Keine Ausnahme, keine Begründung — "
    "wenn dort „Arabisch“ steht, antworte von der ersten bis zur letzten Zeile auf Arabisch.\n\n"
    "STRUKTUR DEINER ANTWORT (in der geforderten Sprache):\n"
    "1. KURZ ZUSAMMENGEFASST: Was steht im Brief? (Betreff, Absender, Kernaussage in 2–3 Sätzen.)\n"
    "2. RECHTSGRUNDLAGE: Welcher Paragraph aus dem KONTEXT passt? Nenne die genaue Norm (z.B. § 199a SGB V). Nur aus dem KONTEXT.\n"
    "3. BETRÄGE UND FRISTEN: Exakt die genannten Beträge und Fristen.\n"
    "4. WAS SOLL DER NUTZER TUN? Konkrete Handlungsempfehlung.\n"
    "5. RECHTE: Seine Rechte in dieser Sache.\n"
    "6. KONSEQUENZEN: Was passiert bei Fristversäumnis oder Ignorieren der Forderung?\n\n"
    "Keine Erfindungen — nur aus Brief und KONTEXT.\n\n"
    "KONTEXT (Gesetze):\n{context_str}\n\n"
    "NUTZERANFRAGE (erste Zeile = Ausgabesprache) und BRIEF:\n{query_str}\n\n"
    "Deine Beratung (vollständig in der geforderten Sprache):"
)
class IndexNotFoundError(RuntimeError):
    pass


class _HybridRetriever(BaseRetriever):
    """Vector + BM25; score merge, dedup by node_id, top_k by combined score."""
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

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable is required for the LLM.")
    llm = Groq(
        model=LLM_MODEL_NAME,
        api_key=api_key,
        request_timeout=RAG_REQUEST_TIMEOUT_SECONDS,
    )
    response_synthesizer = get_response_synthesizer(
        llm=llm,
        text_qa_template=LEGAL_CONSULTANT_PROMPT,
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


def handle_legal_query_with_index(text: str, target_language: str = "Deutsch") -> dict:
    # Engine has no template_vars; language instruction must be in query text
    if target_language == "Arabisch":
        prefix = "AUSGABESPACHE: NUR ARABISCH. Der Nutzer hat Arabisch gewählt. Deine gesamte Antwort MUSS auf Arabisch sein.\n\nBrief:\n"
    else:
        prefix = "AUSGABESPACHE: NUR DEUTSCH.\n\nBrief:\n"
    query_with_lang = prefix + text
    response = _get_query_engine().query(query_with_lang)
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
