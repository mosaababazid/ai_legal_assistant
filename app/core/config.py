from __future__ import annotations

import os
from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parents[2]
APP_DIR: Path = BASE_DIR / "app"
DATA_DIR: Path = BASE_DIR / "data"

DATA_RAW_LAWS_DIR: Path = DATA_DIR / "raw_laws"
DATA_INDEX_DIR: Path = DATA_DIR / "index_store"

# RAG / LLM configuration
EMBEDDING_MODEL_NAME: str = "nomic-embed-text"
LLM_MODEL_NAME: str = "llama3"
RAG_REQUEST_TIMEOUT_SECONDS: int = 1200
RAG_SIMILARITY_TOP_K: int = 5

# Environment
APP_ENV: str = os.getenv("APP_ENV", "development")
IS_PRODUCTION: bool = APP_ENV.lower() == "production"

