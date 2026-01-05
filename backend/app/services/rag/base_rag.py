# backend/app/services/rag/base_rag.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.document import DocumentChunk

class BaseRAG(ABC):
    @abstractmethod
    def add_documents(self, documents: List[DocumentChunk], **kwargs) -> bool:
        """Add multiple document chunks"""
        pass
    
    @abstractmethod
    def add_document(self, doc_id: str, chunks: List[Dict], metadata: Optional[Dict] = None) -> bool:
        """Add a single document with chunks"""
        pass
    
    @abstractmethod
    def search(self, query: str, k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search for relevant chunks"""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response"""
        pass