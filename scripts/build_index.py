from pathlib import Path
import logging
import sys

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.ollama import OllamaEmbedding

# Ensure project root is on sys.path when invoked as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import DATA_RAW_LAWS_DIR, DATA_INDEX_DIR

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


if __name__ == "__main__":
    configure_logging()
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

    DATA_RAW_LAWS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    documents = SimpleDirectoryReader(str(DATA_RAW_LAWS_DIR)).load_data()

    index = VectorStoreIndex.from_documents(documents)

    index.storage_context.persist(persist_dir=str(DATA_INDEX_DIR))

    logger.info("Legal index created and persisted successfully at %s.", DATA_INDEX_DIR)

