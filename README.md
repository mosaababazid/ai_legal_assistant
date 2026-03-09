# AI Legal Assistant

AI Legal Assistant is an AI tool designed to **help Arab refugees and non-German speakers simplify and understand complex German bureaucratic documents (Amtsdeutsch)**.

It reduces misunderstandings by extracting text from letters, producing a concise German summary, and optionally translating the result into Arabic. For legal-oriented questions, it uses **Retrieval-Augmented Generation (RAG)** grounded in a local corpus of German laws to avoid "made up" answers.

## Core Logic & Language Processing

The AI Assistant performs all core analysis and summarization in **German** to ensure maximum legal accuracy. Legal documents, bureaucratic language (Amtsdeutsch), and German law texts require precise interpretation that is best achieved when the AI processes content in its original language. The system extracts text from PDFs or images, cleans and summarizes it in German, and then applies RAG-based legal analysis using a German law corpus.

**Arabic translation** is provided as an optional feature to help Arab refugees and newcomers bridge the language gap. After the German analysis is complete, users can choose to have the summary or legal recommendation translated into Arabic, making the information accessible to those who are still learning German or need immediate comprehension in their native language.

## Tech Stack

- **Backend**: Python, FastAPI, Uvicorn
- **RAG**: LlamaIndex, Ollama (LLM). Embedding and LLM models are configurable in `backend/app/core/config.py`—you can choose whatever models suit you; you're not required to use the same ones as this project.
- **OCR**: EasyOCR, Pillow, NumPy
- **PDF parsing**: PyMuPDF
- **Translation**: Transformers + Torch (German -> Arabic)
- **Frontend**: **Next.js 15** (App Router, React 19, Tailwind) in `web/` (frontend)

## Architecture (RAG Pipeline)

- **Ingestion**: German law texts are scraped (optional) and stored as plain `.txt` files in `backend/data/raw_laws/`.
- **Embedding**: `backend/scripts/build_index.py` creates a vector index and stores it in `backend/data/index_store/`.
- **Retrieval**: At query time, LlamaIndex retrieves the most similar law passages from the persisted index.
- **Generation**: An Ollama LLM generates a German response constrained by a strict prompt to only use retrieved passages.

## Mission (Social Impact)

German bureaucracy is hard even for native speakers. For refugees and newcomers, it can be risky: unclear letters can lead to missed deadlines, lost benefits, or avoidable penalties.

This project focuses on:

- **Immediate comprehension**: OCR/PDF text extraction and clear summarization of bureaucratic letters in German, ensuring legal accuracy.
- **Language access**: Optional German-to-Arabic translation to bridge the language gap quickly, helping Arab refugees understand complex Amtsdeutsch without losing legal precision.
- **Grounded legal context**: RAG-backed responses grounded in an explicit local corpus to reduce hallucinations and provide reliable legal guidance.

By making German bureaucratic documents accessible and understandable, this tool helps prevent misunderstandings that could result in missed legal deadlines, lost social benefits, or unnecessary penalties—critical support for people navigating a new legal system.

## Project Layout

The repo is split into two parts:

- **`backend/`** — Python FastAPI API (OCR, PDF, summarization, translation, RAG)
  - `app/main.py`: FastAPI entry point
  - `app/api/`, `app/services/`, `app/core/`, `app/utils/`
  - `scripts/`: `law_scraper.py`, `build_index.py`
  - `data/`: `raw_laws/`, `index_store/`
- **`web/`** — Next.js 15 frontend (App Router, React 19, Tailwind)

See **`backend/README.md`** and **`web/README.md`** for per-project setup and run instructions.

## Setup & Run

### Prerequisites

- Python 3.11+ (for backend)
- Node.js 18+ (for frontend)
- [Ollama](https://ollama.com) installed and running. Pull whatever LLM you prefer (e.g. `ollama pull llama3.2:3b`). Embedding model is set in `backend/app/core/config.py` (default: HuggingFace multilingual); you can change it to suit your setup.

### Backend

From the **`backend/`** directory:

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
# Optional: python scripts/law_scraper.py && python scripts/build_index.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API: **http://127.0.0.1:8000/**

### Frontend

From the **`web/`** directory:

```bash
cd web
cp .env.local.example .env.local
npm install
npm run dev
```

Open **http://localhost:3000/** and ensure the backend is running at `http://127.0.0.1:8000`. To use another API URL, set `NEXT_PUBLIC_API_URL` in `web/.env.local`.

## Usage

1. **Upload a document**: Select a PDF or image file containing German bureaucratic text.
2. **Choose language**: Select German (Deutsch) or Arabic (Arabisch) for the output language.
3. **Select mode**:
   - **Nur Zusammenfassung**: Extracts and summarizes the document text.
   - **Zusammenfassung + rechtliche Einordnung**: Provides summary plus RAG-based legal analysis using the German law corpus.

The system will extract text, clean it, summarize it in German, and optionally translate the result to Arabic if requested. Legal analysis mode requires the vector index to be built (step 4 in Setup).
