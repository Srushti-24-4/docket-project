"""Extraction path for .txt / .md files — just decode and return as one page."""


def extract_text(file_bytes: bytes) -> list[dict]:
    text = file_bytes.decode("utf-8", errors="replace")
    return [{"page": 1, "text": text}]
