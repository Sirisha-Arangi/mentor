# backend/rag_singleton.py
import logging
from app.services.rag import RAGFactory
from app.config import settings

logger = logging.getLogger(__name__)

# Singleton instance for LangChain RAG service
_rag_service = None

def get_rag_service():
    """Get LangChain RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGFactory.create_rag_service(
            provider="langchain",
            api_key=settings.GEMINI_API_KEY
        )
        logger.info("Created LangChain RAG service singleton")
    return _rag_service