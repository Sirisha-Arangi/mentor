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

# Global RAG service instances for backward compatibility
_custom_rag_service = None
_langchain_rag_service = None

def get_rag_service(provider: str = "chroma_gemini"):
    """Get RAG service instance with provider selection"""
    global _custom_rag_service, _langchain_rag_service
    
    if provider == "langchain":
        if _langchain_rag_service is None:
            from app.services.rag import RAGFactory
            _langchain_rag_service = RAGFactory.create_rag_service(
                provider="langchain",
                api_key=settings.GEMINI_API_KEY
            )
            logger.info("Created LangChain RAG service")
        return _langchain_rag_service
    
    else:  # Default to custom
        if _custom_rag_service is None:
            from app.services.rag import RAGFactory
            _custom_rag_service = RAGFactory.create_rag_service(
                provider="chroma_gemini",
                api_key=settings.GEMINI_API_KEY
            )
            logger.info("Created custom RAG service")
        return _custom_rag_service

@app.get("/")
async def root():
    return {"message": "AI Teaching Assistant API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Teaching Assistant"}

@app.get("/api/rag-status")
async def rag_status():
    """Get status of both RAG services"""
    try:
        custom_rag = get_rag_service("chroma_gemini")
        langchain_rag = get_rag_service("langchain")
        
        custom_stats = {}
        langchain_stats = {}
        
        # Get custom RAG stats
        if hasattr(custom_rag, 'get_collection_stats'):
            custom_stats = custom_rag.get_collection_stats()
        else:
            custom_stats = {"status": "available", "type": "custom"}
        
        # Get LangChain RAG stats
        if hasattr(langchain_rag, 'get_collection_stats'):
            langchain_stats = langchain_rag.get_collection_stats()
        else:
            langchain_stats = {"status": "available", "type": "langchain"}
        
        return {
            "custom_rag": custom_stats,
            "langchain_rag": langchain_stats,
            "status": "both_services_available"
        }
        
    except Exception as e:
        logger.error(f"Error getting RAG status: {str(e)}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)