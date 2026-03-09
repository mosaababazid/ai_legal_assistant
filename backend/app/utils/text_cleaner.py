import re


def clean_extracted_text(text: str) -> str:
    """OCR/letter noise: drop [[...]], names, PLZ, boilerplate lines."""
    lines = text.split("\n")
    cleaned_lines = []
    skip_keywords = [
        "telefon", "telefax", "webseite", "bankverbindung", "iban",
        "bic", "commerzbank", "postanschrift", "versicherungsnummer",
        "bkk firmus", "gottlieb-daimler", "osnabr", "knollstra"
    ]
    text = re.sub(r"\[\[.*?\]\]", "", text)
    text = re.sub(r"\b(Herrn|Frau|Herr)\s+[A-ZÄÖÜ][a-zäöü]+\s+[A-ZÄÖÜ][a-zäöü]+", "", text)
    text = re.sub(r"\b\d{5}\s+\w+", "", text)
    text = re.sub(r"\d{2,}\s*(€|Euro)", "", text)
    text = re.sub(r"\d{10,}", "", text)
    for line in lines:
        line = line.strip()
        if line and not any(skip in line.lower() for skip in skip_keywords):
            cleaned_lines.append(line)
    return " ".join(cleaned_lines)