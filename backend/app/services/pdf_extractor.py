"""Extraction path for normal, text-layer PDFs, using PyMuPDF."""
import fitz  # PyMuPDF


def extract_text_by_page(file_bytes: bytes) -> list[dict]:
    """Returns a list of {"page": int, "text": str} for each page."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        pages.append({"page": i + 1, "text": text})
    doc.close()
    return pages
