# backend/app/services/embedding_service.py
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
import os

class EmbeddingService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.chunks = []
        self.documents = []

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        return self.model.encode(texts, show_progress_bar=True)

    def create_index(self, embeddings: np.ndarray):
        """Create a FAISS index from embeddings."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings.astype('float32'))

    def add_document(self, document: Dict, chunks: List[Dict]):
        """Add a document and its chunks to the store."""
        document_id = len(self.documents)
        self.documents.append(document)
        
        for chunk in chunks:
            self.chunks.append({
                **chunk,
                'document_id': document_id
            })

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar chunks."""
        if not self.index:
            raise ValueError("Index not initialized. Call create_index first.")

        # Generate query embedding
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Get top-k results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0:  # FAISS returns -1 for invalid indices
                chunk = self.chunks[idx]
                results.append({
                    'text': chunk['text'],
                    'score': float(distances[0][i]),
                    'document_id': chunk['document_id'],
                    'document': self.documents[chunk['document_id']]
                })
        return results

    def save_index(self, path: str):
        """Save the FAISS index and metadata."""
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, f"{path}/index.faiss")
        # Save metadata
        import json
        with open(f"{path}/metadata.json", 'w') as f:
            json.dump({
                'documents': self.documents,
                'chunks': self.chunks
            }, f)

    def load_index(self, path: str):
        """Load a saved FAISS index and metadata."""
        self.index = faiss.read_index(f"{path}/index.faiss")
        # Load metadata
        import json
        with open(f"{path}/metadata.json", 'r') as f:
            data = json.load(f)
            self.documents = data['documents']
            self.chunks = data['chunks']