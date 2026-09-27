"""
Extraction path for table-heavy documents (financial reports, statements).

Uses pdfplumber first (fast, no external deps beyond poppler) and falls back
to Camelot's lattice mode for tables with visible ruling lines that
pdfplumber misses. Tables are serialized to markdown so they stay readable
as plain text chunks downstream, and body text on the page is kept too.
"""
import io
import pdfplumber

try:
    import camelot
    HAS_CAMELOT = True
except ImportError:
    HAS_CAMELOT = False


def _table_to_markdown(table: list[list[str | None]]) -> str:
    rows = [[c or "" for c in row] for row in table]
    if not rows:
        return ""
    header, *body = rows
    md = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * len(header)) + " |"]
    for row in body:
        md.append("| " + " | ".join(row) + " |")
    return "\n".join(md)


def extract_text_by_page(file_bytes: bytes) -> list[dict]:
    pages_out = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            body_text = page.extract_text() or ""
            tables = page.extract_tables()
            table_blocks = [_table_to_markdown(t) for t in tables if t]

            combined = body_text
            if table_blocks:
                combined += "\n\n" + "\n\n".join(table_blocks)

            pages_out.append({"page": i + 1, "text": combined})

    if HAS_CAMELOT and all(not p["text"].strip() for p in pages_out):
        # pdfplumber found nothing usable — fall back to Camelot's lattice parser
        tmp_path = "/tmp/_docket_table_extract.pdf"
        with open(tmp_path, "wb") as f:
            f.write(file_bytes)
        tables = camelot.read_pdf(tmp_path, pages="all", flavor="lattice")
        for t in tables:
            page_num = int(t.page)
            md = _table_to_markdown(t.df.values.tolist())
            idx = page_num - 1
            if 0 <= idx < len(pages_out):
                pages_out[idx]["text"] += "\n\n" + md

    return pages_out
