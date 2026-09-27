from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import upload, chat

settings = get_settings()

app = FastAPI(
    title="Docket API",
    description="Document intelligence pipeline: routing, extraction, embedding, and cited Q&A.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}
