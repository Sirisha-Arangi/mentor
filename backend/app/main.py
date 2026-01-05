from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
from typing import List
import uuid

from app.services.document_processor import DocumentProcessor
from app.services.rag import RAGFactory
from app.config import settings

app = FastAPI(title="AI Teaching Assistant API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
rag_service = RAGFactory.create_rag_service(
    api_key=settings.GEMINI_API_KEY,
    collection_name="academic_docs",
    persist_directory="./chroma_data"
)
doc_processor = DocumentProcessor()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile):
    """Upload and process a document"""
    try:
        # Save the uploaded file
        file_extension = os.path.splitext(file.filename)[1]
        document_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{document_id}{file_extension}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the document
        chunks = await doc_processor.process_document(str(file_path), document_id)
        
        # Convert to DocumentChunk objects
        from app.services.rag import DocumentChunk
        document_chunks = [
            DocumentChunk(
                text=chunk['text'],
                metadata=chunk['metadata']
            )
            for chunk in chunks
        ]
        
        # Add to vector store
        await rag_service.add_documents(document_chunks)
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "num_chunks": len(chunks),
            "status": "processed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/query")
async def query_document(query: str, document_id: str = None):
    """Query the document using RAG"""
    try:
        filters = {"document_id": document_id} if document_id else None
        response = await rag_service(
            query=query,
            k=5,
            filters=filters,
            temperature=0.7,
            max_tokens=500
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)