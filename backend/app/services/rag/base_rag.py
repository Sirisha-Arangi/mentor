from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pydantic import BaseModel

class DocumentChunk(BaseModel):
    text: str
    metadata: dict
    embedding: Optional[List[float]] = None

class BaseRAG(ABC):
    @abstractmethod
    async def add_documents(self, documents: List[DocumentChunk]) -> None:
        """Add documents to the vector store"""
        pass
    
    @abstractmethod
    async def search(
        self, 
        query: str, 
        k: int = 5,
        filters: Optional[Dict] = None
    ) -> List[DocumentChunk]:
        """Search for relevant document chunks"""
        pass
    
    @abstractmethod
    async def generate(
        self,
        query: str,
        context: List[DocumentChunk],
        **generation_params
    ) -> str:
        """Generate response using LLM with RAG"""
        pass

    async def __call__(
        self,
        query: str,
        k: int = 5,
        filters: Optional[Dict] = None,
        **generation_params
    ) -> str:
        """Complete RAG pipeline"""
        context = await self.search(query, k, filters)
        return await self.generate(query, context, **generation_params)