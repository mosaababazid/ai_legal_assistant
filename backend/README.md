# AI Legal Assistant — Backend

FastAPI backend: OCR, PDF extraction, summarization and RAG, optional DEtoAR translation, law corpus in `data/raw_laws`, index in `data/index_store`. Default LLM is Groq; you can switch to any LlamaIndex-compatible LLM (e.g. Ollama for local).

## Prerequisites

- Python 3.11+
- **LLM**: Default is Groq — set `GROQ_API_KEY` in `.env` (see `.env.example`). For another provider or local (e.g. Ollama), see **Choosing the LLM** below.

## Setup

1. **From this directory (`backend/`)**, create and activate a virtual environment (use a venv here, not the old one from the project root; `__pycache__` and `.venv` are gitignored):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Add `GROQ_API_KEY` to `.env` (see `.env.example`).

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional)** Add law texts to `data/raw_laws/` (`.txt` or `.xml`), then build index:
   ```bash
   python scripts/build_index.py
   ```
   Required for "Zusammenfassung + rechtliche Einordnung".

## Choosing the LLM

The project ships with **Groq** as the default LLM. You can use any other model or run locally:

- **Model name** and timeout: `app/core/config.py` (`LLM_MODEL_NAME`, `RAG_REQUEST_TIMEOUT_SECONDS`).
- **Provider**: Implementations live in `app/services/rag_service.py` and `app/services/summarization_service.py`. Swap the LlamaIndex LLM (e.g. `Groq` to `Ollama`) and install the matching package (e.g. `pip install llama-index-llms-ollama`). Keep the same config keys so the rest of the pipeline stays unchanged.

Example for **local Ollama**: set `LLM_MODEL_NAME` to your pulled model (e.g. `llama3.2:3b`), replace the Groq client with Ollama in both services, and remove the `GROQ_API_KEY` requirement.

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
