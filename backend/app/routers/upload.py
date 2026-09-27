import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.core.config import get_settings
from app.core.security import get_current_user_id
from app.models.schemas import UploadedDocument, DocumentRoute
from app.services import router as doc_router
from app.services import (
    pdf_extractor,
    ocr,
    table_extractor,
    image_extractor,
    docx_extractor,
    text_extractor,
    chunker,
    embeddings,
    vector_store,
    storage,
)

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()

ALLOWED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".docx", ".txt", ".md",
}

# Route -> extractor. PDF sub-routes reuse the same three extractors as before;
# the new routes each have a single dedicated extractor.
PDF_EXTRACTORS = {
    DocumentRoute.normal_pdf: pdf_extractor.extract_text_by_page,
    DocumentRoute.scanned_pdf: ocr.extract_text_by_page,
    DocumentRoute.table_heavy: table_extractor.extract_text_by_page,
}


@router.post("", response_model=UploadedDocument)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
) -> UploadedDocument:
    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.max_upload_mb:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb}MB limit")

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    document_id = str(uuid.uuid4())

    # 1. Route
    try:
        route = doc_router.classify_upload(file.filename, file_bytes)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    # 2. Extract using the matching path
    if route in PDF_EXTRACTORS:
        pages = PDF_EXTRACTORS[route](file_bytes)
    elif route == DocumentRoute.image:
        pages = image_extractor.extract_text(file_bytes)
    elif route == DocumentRoute.docx:
        pages = docx_extractor.extract_text(file_bytes)
    elif route == DocumentRoute.plain_text:
        pages = text_extractor.extract_text(file_bytes)
    else:
        raise HTTPException(500, f"No extractor registered for route {route}")

    # 3. Chunk
    chunks = chunker.chunk_pages(pages, document_id, user_id, file.filename, route)

    # 4. Embed + store in Qdrant
    if chunks:
        vectors = embeddings.embed_documents([c.text for c in chunks])
        vector_store.upsert_chunks(chunks, vectors)

    # 5. Persist file + metadata in Supabase
    storage_path = storage.upload_file(document_id, user_id, file.filename, file_bytes)
    doc = UploadedDocument(
        id=document_id,
        user_id=user_id,
        filename=file.filename,
        route=route,
        page_count=len(pages),
        storage_path=storage_path,
    )
    storage.save_document_record(doc)

    return doc


@router.get("", response_model=list[UploadedDocument])
async def list_documents(user_id: str = Depends(get_current_user_id)) -> list[UploadedDocument]:
    return storage.list_documents(user_id)


@router.get("/{document_id}", response_model=UploadedDocument)
async def get_document(
    document_id: str,
    user_id: str = Depends(get_current_user_id),
) -> UploadedDocument:
    doc = storage.get_document(document_id, user_id)
    if doc is None:
        raise HTTPException(404, "Document not found")
    return doc
