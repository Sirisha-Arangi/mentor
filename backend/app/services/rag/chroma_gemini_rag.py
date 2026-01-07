# backend/app/services/rag/chroma_gemini_rag.py
import google.generativeai as genai
from typing import List, Dict, Any
from .chroma_rag import ChromaRAG
from app.models.document import DocumentChunk
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class ChromaGeminiRAG(ChromaRAG):
    def __init__(
        self,
        api_key: str,
        model_name: str = None,
        collection_name: str = "academic_docs",
        persist_directory: str = "./chroma_data",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        super().__init__(collection_name, persist_directory, embedding_model)
        
        # Initialize Gemini
        self.model_name = model_name or settings.MODEL_NAME
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        logger.info(f"Initialized ChromaGeminiRAG with model: {self.model_name}")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Gemini"""
        try:
            logger.info(f"Generating response with prompt length: {len(prompt)}")
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = f"Error in generation: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg

    def add_documents(self, documents: List[DocumentChunk], **kwargs) -> bool:
        """Add documents using parent class method"""
        return super().add_documents(documents, **kwargs)

    def search(self, query: str, k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search using parent class method"""
        return super().search(query, k, **kwargs)