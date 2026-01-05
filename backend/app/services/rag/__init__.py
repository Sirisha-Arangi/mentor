from .base_rag import BaseRAG
from .gemini_rag import GeminiRAG
from app.config import settings

class RAGFactory:
    @staticmethod
    def create_rag_service(provider: str = "gemini", **kwargs) -> BaseRAG:
        provider = provider.lower()

        if provider == "gemini":
            api_key = kwargs.pop("api_key", None) or settings.GEMINI_API_KEY
            model_name = kwargs.pop("model_name", None) or settings.MODEL_NAME
            return GeminiRAG(api_key=api_key, model_name=model_name, **kwargs)

        raise ValueError(f"Unsupported RAG provider: {provider}")