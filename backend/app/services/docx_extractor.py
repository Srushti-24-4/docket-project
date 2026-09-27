"""Extraction path for .docx files, using python-docx.

Word documents don't have "pages" in the PDF sense (pagination depends on
the viewer/printer), so the whole document is treated as a single page for
citation purposes — page 1 always refers to the full document.
"""
import io
from docx import Document


def extract_text(file_bytes: bytes) -> list[dict]:
    doc = Document(io.BytesIO(file_bytes))

    parts = [p.text for p in doc.paragraphs if p.text.strip()]

    for table in doc.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells]
            if any(cells):
                parts.append(" | ".join(cells))

    return [{"page": 1, "text": "\n".join(parts)}]
