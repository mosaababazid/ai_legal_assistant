# AI Legal Assistant — Backend

FastAPI backend: OCR, PDF extraction, summarization (Ollama), German to Arabic translation, and RAG over German law corpus.

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running. Pull the LLM you use (see `app/core/config.py`); default is `tinyllama`:
  ```bash
  ollama pull tinyllama
  ```
  Embedding is HuggingFace (no Ollama pull needed for that).

## Setup

1. **From this directory (`backend/`)**, create and activate a virtual environment (use a venv here, not the old one from the project root; `__pycache__` and `.venv` are gitignored):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional)** Scrape German law texts for RAG:
   ```bash
   python scripts/law_scraper.py
   ```

4. **(Optional)** Build the vector index (required for "Zusammenfassung + rechtliche Einordnung"):
   ```bash
   python scripts/build_index.py
   ```

## Run

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API: **http://127.0.0.1:8000/**  
Docs: **http://127.0.0.1:8000/docs**

## Layout

- `app/` — FastAPI app, API routes, services (OCR, PDF, summarization, translation, RAG)
- `scripts/` — `law_scraper.py`, `build_index.py`
- `data/` — `raw_laws/`, `index_store/` (created at runtime if missing)
