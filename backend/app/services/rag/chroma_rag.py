import chromadb
from typing import List, Optional, Dict
from .base_rag import BaseRAG, DocumentChunk
from chromadb.config import Settings

class ChromaRAG(BaseRAG):
    def __init__(
        self,
        collection_name: str = "academic_docs",
        persist_directory: str = "./chroma_data"
    ):
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(allow_reset=True)
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_model = None  # Will be set by child classes

    async def add_documents(self, documents: List[DocumentChunk]) -> None:
        """Add documents to ChromaDB"""
        if not documents:
            return

        ids = [str(i) for i in range(len(documents))]
        embeddings = [doc.embedding for doc in documents if doc.embedding]
        texts = [doc.text for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        if embeddings:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
        else:
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )

    async def search(
        self,
        query: str,
        k: int = 5,
        filters: Optional[Dict] = None
    ) -> List[DocumentChunk]:
        """Search for relevant document chunks"""
        if self.embedding_model:
            query_embedding = self.embedding_model.embed_query(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=filters
            )
        else:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=filters
            )

        chunks = []
        for i in range(len(results.get('documents', [[]])[0])):
            chunks.append(DocumentChunk(
                text=results['documents'][0][i],
                metadata=results['metadatas'][0][i],
                embedding=results.get('embeddings', [None])[0][i] if 'embeddings' in results else None
            ))
        return chunks