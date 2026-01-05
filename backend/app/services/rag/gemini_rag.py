# backend/app/services/rag/gemini_rag.py
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from .base_rag import BaseRAG
from app.models.document import DocumentChunk
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class GeminiRAG(BaseRAG):
    def __init__(self, api_key: str, model_name: str | None = None, **kwargs):
        super().__init__()
        self.model_name = model_name or settings.MODEL_NAME
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)
        self.chunks: List[DocumentChunk] = []
        self.documents: Dict[str, Any] = {}
        logger.info(f"Initialized GeminiRAG with model: {self.model_name}")

    def add_documents(self, documents: List[DocumentChunk], **kwargs) -> bool:
        """Add multiple document chunks to the RAG system."""
        try:
            logger.info(f"Adding {len(documents)} document chunks")
            self.chunks.extend(documents)
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}", exc_info=True)
            return False

    def add_document(self, doc_id: str, chunks: List[Dict], metadata: Optional[Dict] = None) -> bool:
        """Add a document with multiple chunks to the RAG system."""
        try:
            logger.info(f"Adding document {doc_id} with {len(chunks)} chunks")
            self.documents[doc_id] = {
                "chunks": [chunk['text'] for chunk in chunks],
                "metadata": metadata or {}
            }
            # Convert dicts to DocumentChunk objects
            doc_chunks = []
            for i, chunk in enumerate(chunks):
                doc_chunks.append(DocumentChunk(
                    text=chunk['text'],
                    document_id=doc_id,
                    metadata={
                        **chunk.get('metadata', {}),
                        "chunk_index": i,
                        "doc_id": doc_id
                    }
                ))
            
            self.chunks.extend(doc_chunks)
            return True
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}", exc_info=True)
            return False

    def search(self, query: str, k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search for relevant document chunks based on the query."""
        try:
            logger.info(f"Searching for query: {query}")
            # Simple implementation: return the first k chunks
            results = []
            for chunk in self.chunks[:k]:
                results.append(chunk.dict())
            return results
        except Exception as e:
            logger.error(f"Error in search: {str(e)}", exc_info=True)
            return []

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response based on the prompt."""
        try:
            logger.info(f"Generating response for prompt: {prompt[:100]}...")
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = f"Error in generation: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg