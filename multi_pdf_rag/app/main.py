import sys
from pathlib import Path

from fastapi import FastAPI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.routes.upload import router as upload_router
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router

app = FastAPI(
    title="Production Multi PDF RAG"
)

app.include_router(upload_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(health_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "RAG API Running"
    }