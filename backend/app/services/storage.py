"""
Supabase-backed storage.

Uploaded files go to Supabase Storage; document metadata (route, page
count, storage path) goes to a `documents` table in Supabase Postgres.
See supabase_schema.sql for the table definition.
"""
from fastapi import HTTPException
from supabase import create_client, Client
from app.core.config import get_settings
from app.models.schemas import UploadedDocument, DocumentRoute

settings = get_settings()

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise HTTPException(
                500,
                "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is missing in backend/.env",
            )
        _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _client


def upload_file(document_id: str, user_id: str, filename: str, file_bytes: bytes) -> str:
    client = get_client()
    storage_path = f"{user_id}/{document_id}/{filename}"
    try:
        client.storage.from_(settings.supabase_storage_bucket).upload(
            storage_path, file_bytes, {"content-type": "application/octet-stream"}
        )
    except Exception as exc:
        raise HTTPException(
            502,
            "Supabase Storage upload failed. Check SUPABASE_URL, "
            "SUPABASE_SERVICE_ROLE_KEY, and that a bucket named "
            f"'{settings.supabase_storage_bucket}' exists. "
            f"Original error: {exc!r}",
        ) from exc
    return storage_path


def save_document_record(doc: UploadedDocument) -> None:
    client = get_client()
    try:
        client.table("documents").insert(
            {
                "id": doc.id,
                "user_id": doc.user_id,
                "filename": doc.filename,
                "route": doc.route.value,
                "page_count": doc.page_count,
                "storage_path": doc.storage_path,
            }
        ).execute()
    except Exception as exc:
        raise HTTPException(
            502,
            "Supabase table insert failed. Did you run supabase_schema.sql "
            f"in the SQL editor yet? Original error: {exc!r}",
        ) from exc


def list_documents(user_id: str) -> list[UploadedDocument]:
    client = get_client()
    rows = (
        client.table("documents")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return [_row_to_document(row) for row in rows.data]


def get_document(document_id: str, user_id: str) -> UploadedDocument | None:
    client = get_client()
    rows = (
        client.table("documents")
        .select("*")
        .eq("id", document_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not rows.data:
        return None
    return _row_to_document(rows.data[0])


def _row_to_document(row: dict) -> UploadedDocument:
    return UploadedDocument(
        id=row["id"],
        user_id=row["user_id"],
        filename=row["filename"],
        route=DocumentRoute(row["route"]),
        page_count=row["page_count"],
        storage_path=row["storage_path"],
    )
