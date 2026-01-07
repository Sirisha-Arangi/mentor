from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import documents
from app.services.rag import RAGFactory
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Document Summarizer API")

# Configure CORS - Allow all localhost origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all localhost origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG service instance
rag_service = None

def get_rag_service():
    global rag_service
    if rag_service is None:
        logger.info("Creating ChromaDB + Gemini RAG service...")
        rag_service = RAGFactory.create_rag_service(
            provider="chroma_gemini",
            collection_name="academic_docs",
            persist_directory="./chroma_data"
        )
        logger.info("RAG service created successfully")
    return rag_service

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])

@app.get("/api/rag-status")
async def rag_status():
    service = get_rag_service()
    stats = service.get_collection_stats() if hasattr(service, 'get_collection_stats') else {}
    return {
        "rag_initialized": service is not None, 
        "total_chunks": stats.get("total_documents", 0),
        "collection_name": stats.get("collection_name", "unknown"),
        "provider": "chroma_gemini"
    }