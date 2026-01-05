from typing import List, Optional, Dict
import google.generativeai as genai
from .chroma_rag import ChromaRAG
from .base_rag import DocumentChunk

class GeminiRAG(ChromaRAG):
    def __init__(
        self,
        api_key: str,
        embedding_model: str = "models/embedding-001",
        chat_model: str = "gemini-pro",
        **kwargs
    ):
        super().__init__(**kwargs)
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        self.embedding_model_name = embedding_model
        self.chat_model_name = chat_model

    async def embed_query(self, text: str) -> List[float]:
        """Generate embedding using Gemini's embedding model"""
        try:
            result = genai.embed_content(
                model=self.embedding_model_name,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 768  # Fallback zero vector

    async def generate(
        self,
        query: str,
        context: List[DocumentChunk],
        system_prompt: str = "You are a helpful AI teaching assistant.",
        **generation_params
    ) -> str:
        """Generate response using Gemini's chat model"""
        try:
            # Prepare context
            context_text = "\n\n".join([doc.text for doc in context])
            
            # Create the model
            model = genai.GenerativeModel(self.chat_model_name)
            
            # Prepare the prompt
            prompt = f"""{system_prompt}
            
            Context:
            {context_text}
            
            Question: {query}
            
            Answer:"""
            
            # Generate content
            response = await model.generate_content_async(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error in Gemini generation: {e}")
            return f"An error occurred: {str(e)}"