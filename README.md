# AI Legal Assistant

AI Legal Assistant is an AI tool designed to **help Arab refugees and non-German speakers simplify and understand complex German bureaucratic documents (Amtsdeutsch)**.

It reduces misunderstandings by extracting text from letters, producing a concise German summary, and optionally translating the result into Arabic. For legal-oriented questions, it uses **Retrieval-Augmented Generation (RAG)** grounded in a local corpus of German laws to avoid "made up" answers.

## Core Logic & Language Processing

The AI Assistant performs all core analysis and summarization in **German** to ensure maximum legal accuracy. Legal documents, bureaucratic language (Amtsdeutsch), and German law texts require precise interpretation that is best achieved when the AI processes content in its original language. The system extracts text from PDFs or images, cleans and summarizes it in German, and then applies RAG-based legal analysis using a German law corpus.

**Arabic translation** is provided as an optional feature to help Arab refugees and newcomers bridge the language gap. After the German analysis is complete, users can choose to have the summary or legal recommendation translated into Arabic, making the information accessible to those who are still learning German or need immediate comprehension in their native language.

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

- **Immediate comprehension**: OCR/PDF text extraction and clear summarization of bureaucratic letters in German, ensuring legal accuracy.
- **Language access**: Optional German-to-Arabic translation to bridge the language gap quickly, helping Arab refugees understand complex Amtsdeutsch without losing legal precision.
- **Grounded legal context**: RAG-backed responses grounded in an explicit local corpus to reduce hallucinations and provide reliable legal guidance.

By making German bureaucratic documents accessible and understandable, this tool helps prevent misunderstandings that could result in missed legal deadlines, lost social benefits, or unnecessary penalties—critical support for people navigating a new legal system.

## Project Layout

- `app/main.py`: FastAPI application entry point with CORS configuration
- `app/api/`: API endpoints and route handlers
  - `routes.py`: Main upload endpoint handling OCR/PDF extraction, summarization, and legal RAG queries
- `app/services/`: Core business logic modules
  - `ocr_service.py`: Image text extraction using EasyOCR
  - `pdf_service.py`: PDF text extraction using PyMuPDF
  - `summarization_service.py`: Text summarization using Ollama LLM
  - `translation_service.py`: German-to-Arabic translation using Transformers
  - `rag_service.py`: RAG-based legal query processing
  - `validation_service.py`: Safety validation for legal responses (RDG-oriented)
- `app/core/`: Application configuration and constants
  - `config.py`: Centralized paths, RAG/LLM settings, and environment configuration
- `app/utils/`: Utility modules
  - `text_cleaner.py`: Text cleaning and sanitization utilities
- `data/`: Data directories (generated artifacts, excluded from git)
  - `raw_laws/`: Source German law documents (plain text files)
  - `index_store/`: Persisted LlamaIndex vector database
- `scripts/`: Utility scripts for data preparation
  - `law_scraper.py`: Scrapes German law texts from gesetze-im-internet.de
  - `build_index.py`: Builds the vector index from law documents
- `frontend/`: Static UI files
  - `index.html`: Main HTML interface
  - `styles.css`: Styling and responsive design
  - `script.js`: Frontend JavaScript logic

## Setup & Run

### Prerequisites

- Python 3.11+ recommended
- Ollama installed and running locally
  - Pull required models:
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
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000/`.

### Frontend

Serve the static UI using a local HTTP server:

```bash
python -m http.server --directory frontend 5173
```

Then open `http://127.0.0.1:5173/` in your browser and upload a PDF or image file.

## Usage

1. **Upload a document**: Select a PDF or image file containing German bureaucratic text.
2. **Choose language**: Select German (Deutsch) or Arabic (Arabisch) for the output language.
3. **Select mode**:
   - **Nur Zusammenfassung**: Extracts and summarizes the document text.
   - **Zusammenfassung + rechtliche Einordnung**: Provides summary plus RAG-based legal analysis using the German law corpus.

The system will extract text, clean it, summarize it in German, and optionally translate the result to Arabic if requested. Legal analysis mode requires the vector index to be built (step 4 in Setup).
