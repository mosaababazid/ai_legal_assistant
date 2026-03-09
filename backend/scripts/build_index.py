# Build RAG index from raw_laws; same logic runs on backend startup
from pathlib import Path
import logging
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.index_builder import build_legal_index

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


if __name__ == "__main__":
    configure_logging()
    build_legal_index()
