"""
Extraction path for scanned / image-only PDFs.

Pipeline: render each page to an image with PyMuPDF -> clean it up with
OpenCV (deskew, denoise, threshold) -> run PaddleOCR to recover text.

PaddleOCR model loading is expensive, so the OCR engine is created once
and reused (see `get_ocr_engine`). `preprocess` and `get_ocr_engine` are
also imported by `image_extractor.py` for standalone image uploads.
"""
import cv2
import numpy as np
import fitz  # PyMuPDF

_ocr_engine = None


def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        from paddleocr import PaddleOCR
        _ocr_engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    return _ocr_engine


def preprocess(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
    )
    return thresh


def _render_page_to_image(page: fitz.Page, zoom: float = 2.0) -> np.ndarray:
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    elif pix.n == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img


def extract_text_by_page(file_bytes: bytes) -> list[dict]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    engine = get_ocr_engine()
    pages = []

    for i, page in enumerate(doc):
        image = _render_page_to_image(page)
        cleaned = preprocess(image)
        result = engine.ocr(cleaned, cls=True)

        lines = []
        for block in result or []:
            for _box, (text, confidence) in block:
                if confidence >= 0.5:
                    lines.append(text)

        pages.append({"page": i + 1, "text": "\n".join(lines)})

    doc.close()
    return pages
