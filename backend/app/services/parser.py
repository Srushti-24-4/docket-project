import os
import fitz  # PyMuPDF
from fastapi import UploadFile, HTTPException
import docx
from PIL import Image
import paddleocr
from paddleocr import PaddleOCR

# Initialize PaddleOCR for handling raw structural text in images
# It will download the lightweight inference models on first run automatically
ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_image(file_path: str) -> str:
    result = ocr.ocr(file_path, cls=True)
    txts = []
    if result and result[0]:
        for line in result[0]:
            txts.append(line[1][0])
    return "\n".join(txts)

async def process_incoming_file(file: UploadFile) -> str:
    extension = os.path.splitext(file.filename)[1].lower()
    temp_path = f"temp_{file.filename}"
    
    # Save file temporarily to disk for processing
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
        
    try:
        if extension == ".pdf":
            text = extract_text_from_pdf(temp_path)
        elif extension in [".docx", ".doc"]:
            text = extract_text_from_docx(temp_path)
        elif extension in [".txt", ".md"]:
            with open(temp_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif extension in [".png", ".jpg", ".jpeg", ".webp"]:
            text = extract_text_from_image(temp_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {extension}")
            
        if not text.strip():
            raise HTTPException(status_code=422, detail="No readable text found inside the document.")
            
        return text
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
