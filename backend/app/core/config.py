from __future__ import annotations

import os
from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parents[2]
APP_DIR: Path = BASE_DIR / "app"
DATA_DIR: Path = BASE_DIR / "data"
DATA_RAW_LAWS_DIR: Path = DATA_DIR / "raw_laws"  # .txt/.xml law texts; source for RAG index
DATA_INDEX_DIR: Path = DATA_DIR / "index_store"  # persisted vector index (build_index / startup)

EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL_NAME: str = "llama-3.3-70b-versatile"  # default Groq; change model + LLM client in rag/summarization services for Ollama or other
RAG_REQUEST_TIMEOUT_SECONDS: int = 120
RAG_SIMILARITY_TOP_K: int = 3  # top-k per retriever before merge

APP_ENV: str = os.getenv("APP_ENV", "development")
IS_PRODUCTION: bool = APP_ENV.lower() == "production"

