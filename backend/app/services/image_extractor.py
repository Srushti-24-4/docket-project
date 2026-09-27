"""Extraction path for standalone image uploads (jpg, png, webp, bmp, tiff).

Reuses the same OpenCV preprocessing and PaddleOCR engine as ocr.py's
scanned-PDF path, just applied to a single image instead of rendered PDF pages.
"""
import cv2
import numpy as np

from app.services.ocr import preprocess, get_ocr_engine


def extract_text(file_bytes: bytes) -> list[dict]:
    """Returns a single-page list, matching the shape other extractors use."""
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image file")

    cleaned = preprocess(image)
    engine = get_ocr_engine()
    result = engine.ocr(cleaned, cls=True)

    lines = []
    for block in result or []:
        for _box, (text, confidence) in block:
            if confidence >= 0.5:
                lines.append(text)

    return [{"page": 1, "text": "\n".join(lines)}]
