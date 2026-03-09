# CORS open for local dev; index built on startup if missing (blocking, ~1–2 min first run)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
import logging

from app.services.index_builder import index_exists, build_legal_index

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def _maybe_build_index() -> None:
    """Build RAG index once if raw_laws has .txt/.xml; else summary-only until next run"""
    if index_exists():
        return
    logger.info("Gesetzesindex fehlt – baue Index jetzt (einmalig, kann 1–2 Min. dauern) …")
    if build_legal_index():
        logger.info("Gesetzesindex fertig.")
    else:
        logger.warning("Index nicht gebaut (keine Gesetzesdateien?). Nur „Nur Zusammenfassung“ nutzbar.")


configure_logging()
app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    _maybe_build_index()

# Allow all for dev; tighten in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)


@app.get("/")
async def root() -> dict:
    return {"message": "API is running correctly."}