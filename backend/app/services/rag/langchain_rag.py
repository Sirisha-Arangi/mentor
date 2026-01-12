# backend/app/services/rag/langchain_rag.py
import logging
from typing import List, Dict, Any, Optional
from app.models.document import DocumentChunk
from app.config import settings

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class LangChainRAG:
    def __init__(
        self,
        api_key: str,
        model_name: str = None,
        collection_name: str = "academic_docs",
        persist_directory: str = "./chroma_data",
        embedding_model: str = "all-MiniLM-L6-v2"  # FIXED: Correct HuggingFace model name
    ):
        self.model_name = model_name or settings.MODEL_NAME
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model
        
        # Initialize LangChain components
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            temperature=0.1
        )
        
        # Use local HuggingFace embeddings (no API limits)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize Chroma vector store
        try:
            self.vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=persist_directory
            )
            logger.info(f"Chroma vector store initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Chroma: {str(e)}")
            # Fallback: create new collection
            self.vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=persist_directory
            )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        logger.info(f"Initialized LangChainRAG with model: {self.model_name}")
        logger.info(f"Using collection: {collection_name}")
        logger.info(f"Embedding model: {embedding_model} (local)")
        logger.info(f"Persist directory: {persist_directory}")

    def add_documents(self, documents: List[DocumentChunk], **kwargs) -> bool:
        """Add documents to Chroma using LangChain"""
        try:
            # Convert DocumentChunk to LangChain Document
            langchain_docs = []
            for doc_chunk in documents:
                metadata = doc_chunk.metadata.copy()
                metadata.update({
                    "document_id": doc_chunk.document_id,
                    "chunk_index": metadata.get("chunk_index", 0)
                })
                
                langchain_doc = Document(
                    page_content=doc_chunk.text,
                    metadata=metadata
                )
                langchain_docs.append(langchain_doc)
            
            # Add to vector store
            self.vectorstore.add_documents(langchain_docs)
            logger.info(f"Added {len(langchain_docs)} documents to LangChain Chroma")
            return True
            
        except Exception as e:
            error_msg = f"Error adding documents to LangChain: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False

    def search(self, query: str, k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search for relevant documents using LangChain"""
        try:
            # Perform similarity search
            docs = self.vectorstore.similarity_search(query, k=k)
            
            # Convert to expected format
            results = []
            for doc in docs:
                results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": 0.0  # LangChain doesn't provide scores by default
                })
            
            logger.info(f"LangChain search found {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            error_msg = f"Error in LangChain search: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return []

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using LangChain LLM"""
        try:
            logger.info(f"LangChain generating response with prompt length: {len(prompt)}")
            
            # Simple invocation for direct prompts
            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            error_msg = f"Error in LangChain generation: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            # Get collection info
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
                "embedding_model": self.embedding_model_name,
                "llm_model": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {
                "collection_name": self.collection_name,
                "document_count": 0,
                "error": str(e)
            }

    def create_retrieval_qa(self, query: str) -> str:
        """Simple RAG implementation without chains"""
        try:
            # Search for relevant documents
            docs = self.vectorstore.similarity_search(query, k=5)
            
            # Combine context
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Generate response with context
            prompt = f"""Based on following context, please answer the question.

Context:
{context}

Question: {query}

Please provide a comprehensive answer based only on the given context."""
            
            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            error_msg = f"Error in retrieval QA: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg