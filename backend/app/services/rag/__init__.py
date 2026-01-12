from .base_rag import BaseRAG
from .langchain_rag import LangChainRAG
from app.config import settings

class RAGFactory:
    @staticmethod
    def create_rag_service(provider: str = "langchain", **kwargs) -> BaseRAG:
        provider = provider.lower()

        if provider == "langchain":
            api_key = kwargs.pop("api_key", None) or settings.GEMINI_API_KEY
            model_name = kwargs.pop("model_name", None) or settings.MODEL_NAME
            collection_name = kwargs.pop("collection_name", "academic_docs")
            persist_directory = kwargs.pop("persist_directory", "./chroma_data")
            embedding_model = kwargs.pop("embedding_model", "all-MiniLM-L6-v2")  # FIXED: Correct model name
            
            return LangChainRAG(
                api_key=api_key,
                model_name=model_name,
                collection_name=collection_name,
                persist_directory=persist_directory,
                embedding_model=embedding_model,
                **kwargs
            )

        raise ValueError(f"Unsupported RAG provider: {provider}")