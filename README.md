# AI Legal Assistant

AI Legal Assistant is an AI tool designed to **help Arab refugees and non-German speakers simplify and understand complex German bureaucratic documents (Amtsdeutsch)**.

It reduces misunderstandings by extracting text from letters, producing a concise German summary, and optionally translating the result into Arabic. For legal-oriented questions, it uses **Retrieval-Augmented Generation (RAG)** grounded in a local corpus of German laws to avoid “made up” answers.

## Tech Stack

- **Backend**: Python, FastAPI, Uvicorn
- **RAG**: LlamaIndex, Ollama (LLM + embeddings)
- **OCR**: EasyOCR, Pillow, NumPy
- **PDF parsing**: PyMuPDF
- **Translation**: Transformers + Torch (German -> Arabic)
- **Frontend**: Static HTML/CSS/JavaScript (served separately)

## Architecture (RAG Pipeline)

- **Ingestion**: German law texts are scraped (optional) and stored as plain `.txt` files in `data/raw_laws/`.
- **Embedding**: `scripts/build_index.py` creates a vector index from those documents using Ollama embeddings and stores it in `data/index_store/`.
- **Retrieval**: At query time, LlamaIndex retrieves the most similar law passages from the persisted index in `data/index_store/`.
- **Generation**: An Ollama LLM generates a German response constrained by a strict prompt to only use retrieved passages.

## Mission (Social Impact)

German bureaucracy is hard even for native speakers. For refugees and newcomers, it can be risky: unclear letters can lead to missed deadlines, lost benefits, or avoidable penalties.

This project focuses on:

- **Immediate comprehension**: OCR/PDF text extraction and clear summarization of bureaucratic letters.
- **Language access**: Optional German-to-Arabic translation to bridge the language gap quickly.
- **Grounded legal context**: RAG-backed responses grounded in an explicit local corpus to reduce hallucinations.

## Project Layout

- `app/main.py`: FastAPI app + CORS setup
- `app/api/routes.py`: Upload endpoint (OCR/PDF -> clean -> summary / legal RAG)
- `app/services/`: OCR, PDF extraction, summarization, translation, RAG service, and safety validation
- `app/core/config.py`: Central configuration (paths, RAG/LLM settings)
- `frontend/`: Static UI (`index.html`, `styles.css`, `script.js`)
- `data/raw_laws/`: Source law documents (plain text)
- `data/index_store/`: Persisted LlamaIndex storage (generated)
- `scripts/`: Helper scripts (`law_scraper.py`, `build_index.py`, `clean.ps1`)

## Setup & Run

### Prerequisites

- Python 3.11+ recommended
- Ollama installed and running locally
  - Pull models as needed (examples):
    - `ollama pull llama3`
    - `ollama pull nomic-embed-text`

### Backend

1. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Scrape German law texts:

```bash
python scripts/law_scraper.py
```

4. Build the vector index:

```bash
python scripts/build_index.py
```

5. Run the API:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000/`.

### Frontend

Open the static UI in your browser:

- Open `frontend/index.html` directly, or
- Serve it via a simple local server (recommended):

```bash
python -m http.server --directory frontend 5173
```

Then open `http://127.0.0.1:5173/` and upload a PDF/image.

## Notes

- The legal response mode is designed to be **grounded in the local index** and includes a safety validation step to reduce overconfident legal claims (RDG-oriented).
- `data/index_store/` and `data/raw_laws/` are generated artifacts (dataset + index). For a clean repo, delete them and regenerate when needed.
- To remove bulky generated artifacts locally (recommended before committing):

```powershell
.\scripts\clean.ps1
```