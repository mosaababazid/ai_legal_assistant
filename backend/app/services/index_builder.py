# RAG index from data/raw_laws (.txt + .xml). Uses embedding model from config;
# you can change EMBEDDING_MODEL_NAME in app/core/config.py to any model that suits you.
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.core.config import (
    DATA_INDEX_DIR,
    DATA_RAW_LAWS_DIR,
    EMBEDDING_MODEL_NAME,
)

logger = logging.getLogger(__name__)

REQUIRED_INDEX_FILES = ["docstore.json", "index_store.json"]


def index_exists() -> bool:
    """True iff index_store has the two files LlamaIndex needs to load"""
    if not DATA_INDEX_DIR.exists():
        return False
    return all((DATA_INDEX_DIR / name).exists() for name in REQUIRED_INDEX_FILES)


def _text_from_xml(path: Path) -> str:
    """Flatten gesetze-im-internet.de XML to plain text (elem.text + elem.tail)"""
    tree = ET.parse(path)
    root = tree.getroot()
    parts = []
    for elem in root.iter():
        if elem.text:
            parts.append(elem.text.strip())
        if elem.tail:
            parts.append(elem.tail.strip())
    return "\n".join(p for p in parts if p)


def _load_raw_law_documents() -> list[Document]:
    """Glob raw_laws for .txt/.xml; return Document list (source filename in metadata)."""
    documents: list[Document] = []
    DATA_RAW_LAWS_DIR.mkdir(parents=True, exist_ok=True)

    for ext in (".txt", ".xml"):
        for path in sorted(DATA_RAW_LAWS_DIR.glob(f"*{ext}")):
            try:
                if ext == ".txt":
                    text = path.read_text(encoding="utf-8", errors="replace").strip()
                else:
                    text = _text_from_xml(path)
                if not text:
                    continue
                documents.append(
                    Document(text=text, metadata={"source": path.name})
                )
                logger.info("Loaded %s (%d chars)", path.name, len(text))
            except Exception as e:
                logger.warning("Skip %s: %s", path.name, e)

    return documents


def build_legal_index() -> bool:
    """Persist vector index to index_store; returns True if built, False if no docs in raw_laws"""
    DATA_RAW_LAWS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    documents = _load_raw_law_documents()
    if not documents:
        logger.warning(
            "No .txt/.xml law files in %s – skipping index build.",
            DATA_RAW_LAWS_DIR,
        )
        return False

    # Chunking: 512 tokens, 100 overlap so legal context is not cut mid-sentence.
    Settings.text_splitter = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=100,
    )
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=EMBEDDING_MODEL_NAME,
    )
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=str(DATA_INDEX_DIR))
    logger.info("Legal index built and saved to %s (%d docs).", DATA_INDEX_DIR, len(documents))
    return True