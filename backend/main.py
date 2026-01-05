from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import documents
from app.services.rag import RAGFactory
from app.config import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Document Summarizer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service once at startup
rag_service = None

@app.on_event("startup")
async def startup_event():
    global rag_service
    try:
        rag_service = RAGFactory.create_rag_service(
            collection_name="academic_docs",
            persist_directory="./chroma_data"
        )
        logger.info("RAG service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {str(e)}", exc_info=True)

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])

# Make rag_service available to endpoints
@app.get("/api/rag-status")
async def rag_status():
    return {"rag_initialized": rag_service is not None, "total_chunks": len(rag_service.chunks) if rag_service else 0}