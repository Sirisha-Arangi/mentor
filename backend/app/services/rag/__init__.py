from typing import Optional
from .gemini_rag import GeminiRAG
from .base_rag import BaseRAG, DocumentChunk

class RAGFactory:
    @staticmethod
    def create_rag_service(
        provider: str = "gemini",
        **kwargs
    ) -> BaseRAG:
        """Create and return a RAG service instance"""
        provider = provider.lower()
        if provider == "gemini":
            return GeminiRAG(**kwargs)
        else:
            raise ValueError(f"Unsupported RAG provider: {provider}")

__all__ = ['RAGFactory', 'BaseRAG', 'DocumentChunk', 'GeminiRAG']