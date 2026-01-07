# backend/app/services/embedding_service.py
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Initialized EmbeddingService with model: {model_name}")

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}", exc_info=True)
            raise

    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query."""
        return self.create_embeddings([query])[0]