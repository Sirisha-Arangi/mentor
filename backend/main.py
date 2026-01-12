from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import documents
from app.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Teaching Assistant",
    description="Generative AI Agent for Automated Teaching Content Creation using RAG",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])

# Global RAG service instance
_rag_service = None

def get_rag_service():
    """Get LangChain RAG service instance"""
    global _rag_service
    if _rag_service is None:
        from app.services.rag import RAGFactory
        _rag_service = RAGFactory.create_rag_service(
            provider="langchain",
            api_key=settings.GEMINI_API_KEY
        )
        logger.info("Created LangChain RAG service")
    return _rag_service

@app.get("/")
async def root():
    return {"message": "AI Teaching Assistant API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Teaching Assistant"}

@app.get("/api/rag-status")
async def rag_status():
    """Get status of LangChain RAG service"""
    try:
        rag_service = get_rag_service()
        
        if hasattr(rag_service, 'get_collection_stats'):
            stats = rag_service.get_collection_stats()
        else:
            stats = {"status": "available", "type": "langchain"}
        
        return {
            "rag_service": stats,
            "provider": "langchain",
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Error getting RAG status: {str(e)}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)