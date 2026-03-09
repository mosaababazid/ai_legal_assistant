from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

# Builds vector index from data/raw_laws (.txt, .xml); persists to data/index_store
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
    if not DATA_INDEX_DIR.exists():
        return False
    return all((DATA_INDEX_DIR / name).exists() for name in REQUIRED_INDEX_FILES)


def _text_from_xml(path: Path) -> str:
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
    DATA_RAW_LAWS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    documents = _load_raw_law_documents()
    if not documents:
        logger.warning(
            "No .txt/.xml law files in %s – skipping index build.",
            DATA_RAW_LAWS_DIR,
        )
        return False

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