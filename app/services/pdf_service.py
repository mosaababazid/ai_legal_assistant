import fitz

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts plain text from a PDF using PyMuPDF (fitz)."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return " ".join(page.get_text() for page in doc)
