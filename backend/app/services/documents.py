from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import documents

app = FastAPI(title="Docket Engine API")

# Mount broad-spectrum local browser context access parameters safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)

@app.get("/")
def read_root():
    return {"status": "online", "message": "Docket Core Backend Services Running"}
