# backend/app/api/endpoints/documents.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os
from pathlib import Path
from datetime import datetime
from app.models.document import Document, DocumentCreate
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.config import settings

router = APIRouter()
embedding_service = EmbeddingService()

@router.post("/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    title: str = None,
    description: str = None
):
    """Upload and process a document."""
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.txt', '.docx']:
        raise HTTPException(400, "Unsupported file type")

    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Save uploaded file
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Process document
    doc_processor = DocumentProcessor()
    file_type = file_ext[1:]  # Remove the dot
    text = doc_processor.extract_text(file_path, file_type)
    cleaned_text = doc_processor.clean_text(text)
    chunks = doc_processor.chunk_text(cleaned_text)

    # Generate embeddings
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embedding_service.create_embeddings(texts)

    # Create document record
    document = Document(
        id=str(len(embedding_service.documents)),
        title=title or Path(file.filename).stem,
        description=description,
        document_type=file_type,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        page_count=len(chunks),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        owner_id="user1"  # TODO: Get from auth
    )

    # Add to vector store
    if not embedding_service.index:
        embedding_service.create_index(embeddings)
    else:
        embedding_service.index.add(embeddings.astype('float32'))
    
    embedding_service.add_document(document.dict(), chunks)

    return document

@router.get("/search")
async def search_documents(query: str, k: int = 5):
    """Search documents using semantic search."""
    results = embedding_service.search(query, k)
    return {"query": query, "results": results}