# Scrape gesetze-im-internet.de HTML to plain text; writes to data/raw_laws/*.txt
import logging
from pathlib import Path
import sys

import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import DATA_RAW_LAWS_DIR

logger = logging.getLogger(__name__)

# Short name to overview URL (soup.get_text; no XML here; for XML use official bulk if needed)
LAWS = {
    "bgb": "https://www.gesetze-im-internet.de/bgb/",
    "stgb": "https://www.gesetze-im-internet.de/stgb/",
    "sgb_1": "https://www.gesetze-im-internet.de/sgb_1/",
    "sgb_2": "https://www.gesetze-im-internet.de/sgb_2/",
    "sgb_3": "https://www.gesetze-im-internet.de/sgb_3/",
    "sgb_4": "https://www.gesetze-im-internet.de/sgb_4/",
    "sgb_5": "https://www.gesetze-im-internet.de/sgb_5/",
    "sgb_6": "https://www.gesetze-im-internet.de/sgb_6/",
    "sgb_7": "https://www.gesetze-im-internet.de/sgb_7/",
    "sgb_8": "https://www.gesetze-im-internet.de/sgb_8/",
    "sgb_9": "https://www.gesetze-im-internet.de/sgb_ix_2001/",
    "sgb_10": "https://www.gesetze-im-internet.de/sgb_10/",
    "sgb_11": "https://www.gesetze-im-internet.de/sgb_11/",
    "stvg": "https://www.gesetze-im-internet.de/stvg/",
    "stvo": "https://www.gesetze-im-internet.de/stvo_2013/",
}


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def scrape_law(name: str, url: str) -> None:
    DATA_RAW_LAWS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        content = soup.get_text(separator="\n")
        cleaned = "\n".join(
            line.strip() for line in content.splitlines() if line.strip()
        )

        filepath = DATA_RAW_LAWS_DIR / f"{name}.txt"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(cleaned, encoding="utf-8")

        logger.info("Saved %s (%s characters)", name, len(cleaned))
    except Exception as exc:
        logger.exception("Failed to scrape %s: %s", name, exc)


if __name__ == "__main__":
    configure_logging()
    for law_name, law_url in LAWS.items():
        scrape_law(law_name, law_url)
    logger.info("All law texts have been saved to %s.", DATA_RAW_LAWS_DIR)

