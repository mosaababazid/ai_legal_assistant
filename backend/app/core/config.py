from __future__ import annotations

import os
from pathlib import Path

# Paths relative to backend/ (parents[2] from app/core/config.py)
BASE_DIR: Path = Path(__file__).resolve().parents[2]
APP_DIR: Path = BASE_DIR / "app"
DATA_DIR: Path = BASE_DIR / "data"
DATA_RAW_LAWS_DIR: Path = DATA_DIR / "raw_laws"
DATA_INDEX_DIR: Path = DATA_DIR / "index_store"

# ---------------------------------------------------------------------------
# Models: you can choose whatever suits you (embedding + LLM). These are the
# defaults used by the project; you are not required to use the same ones.
# - Embedding: used for RAG index build and query; keep the same for index/query.
# - LLM: used for summarization and RAG answers (Ollama). For very low RAM (~5GB)
#   use tinyllama (~638MB). For more RAM try llama3.2:1b, then llama3.2:3b.
#   Tip: set env OLLAMA_NUM_PARALLEL=1 to reduce Ollama memory use.
# ---------------------------------------------------------------------------
EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL_NAME: str = "tinyllama"
RAG_REQUEST_TIMEOUT_SECONDS: int = 1200
# Fewer chunks = less noise; increase if answers miss relevant law.
RAG_SIMILARITY_TOP_K: int = 3

APP_ENV: str = os.getenv("APP_ENV", "development")
IS_PRODUCTION: bool = APP_ENV.lower() == "production"

