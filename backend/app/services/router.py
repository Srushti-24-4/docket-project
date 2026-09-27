"""
Intelligent Document Router.

Step 1: look at the file extension to decide the broad category
  (PDF vs. standalone image vs. Word doc vs. plain text).
Step 2: for PDFs specifically, sample the first few pages to decide
  which of the three PDF extraction paths to use:
    - normal_pdf  -> has a real text layer, few/no large tables -> PyMuPDF
    - scanned_pdf -> little to no extractable text (image-only)  -> OpenCV + PaddleOCR
    - table_heavy -> text layer present but dominated by tables  -> pdfplumber / Camelot
"""
import fitz  # PyMuPDF
from app.models.schemas import DocumentRoute

SAMPLE_PAGES = 3
MIN_CHARS_PER_PAGE_FOR_TEXT = 40

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
DOCX_EXTENSIONS = {".docx"}
TEXT_EXTENSIONS = {".txt", ".md"}


def classify_upload(filename: str, file_bytes: bytes) -> DocumentRoute:
    ext = _extension(filename)

    if ext in IMAGE_EXTENSIONS:
        return DocumentRoute.image
    if ext in DOCX_EXTENSIONS:
        return DocumentRoute.docx
    if ext in TEXT_EXTENSIONS:
        return DocumentRoute.plain_text
    if ext == ".pdf":
        return _classify_pdf(file_bytes)

    raise ValueError(f"Unsupported file type: {ext}")


def _extension(filename: str) -> str:
    idx = filename.rfind(".")
    return filename[idx:].lower() if idx != -1 else ""


def _classify_pdf(file_bytes: bytes) -> DocumentRoute:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages_to_check = min(SAMPLE_PAGES, len(doc))

    total_chars = 0
    total_words_in_tableish_lines = 0
    total_lines = 0

    for i in range(pages_to_check):
        page = doc[i]
        text = page.get_text("text")
        total_chars += len(text.strip())

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            total_lines += 1
            tokens = line.split()
            numeric_tokens = sum(1 for t in tokens if _looks_numeric(t))
            if len(tokens) >= 4 and numeric_tokens >= 2:
                total_words_in_tableish_lines += 1

    doc.close()

    avg_chars_per_page = total_chars / max(pages_to_check, 1)

    if avg_chars_per_page < MIN_CHARS_PER_PAGE_FOR_TEXT:
        return DocumentRoute.scanned_pdf

    if total_lines > 0 and (total_words_in_tableish_lines / total_lines) > 0.35:
        return DocumentRoute.table_heavy

    return DocumentRoute.normal_pdf


def _looks_numeric(token: str) -> bool:
    cleaned = token.replace(",", "").replace("$", "").replace("%", "").replace(".", "")
    return cleaned.isdigit()
