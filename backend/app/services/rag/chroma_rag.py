# backend/app/services/rag/chroma_rag.py
import chromadb
from typing import List, Dict, Any, Optional
from .base_rag import BaseRAG
from app.models.document import DocumentChunk
from app.services.embedding_service import EmbeddingService
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)

class ChromaRAG(BaseRAG):
    def __init__(
        self,
        collection_name: str = "academic_docs",
        persist_directory: str = "./chroma_data",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(allow_reset=True)
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_service = EmbeddingService(embedding_model)
        logger.info(f"Initialized ChromaRAG with collection: {collection_name}")

    def add_documents(self, documents: List[DocumentChunk], **kwargs) -> bool:
        """Add documents to ChromaDB with embeddings"""
        try:
            if not documents:
                return False

            # Generate embeddings for all documents
            texts = [doc.text for doc in documents]
            embeddings = self.embedding_service.create_embeddings(texts)
            
            # Create unique IDs
            ids = [f"{doc.document_id}_{doc.metadata.get('chunk_index', 0)}" for doc in documents]
            
            # Prepare metadata
            metadatas = []
            for doc in documents:
                metadata = doc.metadata.copy() if doc.metadata else {}
                metadata.update({
                    "document_id": doc.document_id,
                    "chunk_index": metadata.get("chunk_index", 0)
                })
                metadatas.append(metadata)

            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {str(e)}", exc_info=True)
            return False

    def search(self, query: str, k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search for relevant document chunks using semantic similarity"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.create_embeddings([query])
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=k
            )
            
            # Format results
            chunks = []
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            for i in range(len(documents)):
                chunks.append({
                    "text": documents[i],
                    "metadata": metadatas[i],
                    "score": 1 - distances[i],  # Convert cosine distance to similarity
                    "document_id": metadatas[i].get("document_id", "")
                })
            
            logger.info(f"Found {len(chunks)} relevant chunks for query")
            return chunks
            
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {str(e)}", exc_info=True)
            return []

    def generate(self, prompt: str, **kwargs) -> str:
        """This method will be implemented by the child class"""
        raise NotImplementedError("ChromaRAG doesn't implement generate. Use ChromaGeminiRAG instead")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"total_documents": 0, "collection_name": self.collection.name}