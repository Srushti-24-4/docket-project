from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr


class DocumentRoute(str, Enum):
    normal_pdf = "normal_pdf"
    scanned_pdf = "scanned_pdf"
    table_heavy = "table_heavy"
    image = "image"            # standalone jpg/png/webp upload, OCR'd directly
    docx = "docx"               # Word documents
    plain_text = "plain_text"    # .txt


class UploadedDocument(BaseModel):
    id: str
    user_id: str
    filename: str
    route: DocumentRoute
    page_count: int
    storage_path: str


class Chunk(BaseModel):
    id: str
    document_id: str
    user_id: str
    filename: str
    page: int
    text: str
    route: DocumentRoute


class SearchResult(BaseModel):
    chunk: Chunk
    score: float


class Citation(BaseModel):
    filename: str
    page: int
    snippet: str
    confidence: float


class ChatRequest(BaseModel):
    question: str
    document_ids: Optional[list[str]] = None
    top_k: int = 8


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    verified: bool


# --- Auth ---

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    access_token: str
    new_password: str


class AuthUser(BaseModel):
    id: str
    email: str
    email_verified: bool


class AuthSession(BaseModel):
    access_token: str
    refresh_token: str
    user: AuthUser


class RegisterResponse(BaseModel):
    message: str
    user: AuthUser
