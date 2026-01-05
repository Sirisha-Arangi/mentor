from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import documents
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Document Summarizer API")

# Configure CORS - FIXED to allow port 5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Added 5173 for Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/documents", tags=["documents"])

@app.get("/api/rag-status")
async def rag_status():
    from rag_singleton import get_rag_service
    rag_service = get_rag_service()
    return {"rag_initialized": rag_service is not None, "total_chunks": len(rag_service.chunks) if rag_service else 0}