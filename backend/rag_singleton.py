from app.services.rag import RAGFactory
import logging

logger = logging.getLogger(__name__)

_rag_service = None

def get_rag_service():
    global _rag_service
    if _rag_service is None:
        logger.info("Creating RAG service singleton...")
        _rag_service = RAGFactory.create_rag_service(
            collection_name="academic_docs",
            persist_directory="./chroma_data"
        )
        logger.info("RAG service singleton created")
    return _rag_service