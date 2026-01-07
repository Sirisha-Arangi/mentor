from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
import logging
import os
import uuid
from pathlib import Path
from pydantic import BaseModel

from app.services.document_processor import DocumentProcessor
from app.models.document import DocumentChunk
from app.config import settings

router = APIRouter()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SummarizeRequest(BaseModel):
    doc_id: str
    style: str = "concise"
    length: str = "medium"


@router.post("/upload")
async def upload_document(file: UploadFile):
    try:
        logger.info(f"Starting upload for file: {file.filename}")

        # Generate unique filename
        file_ext = Path(file.filename).suffix
        file_id = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, file_id)

        # Save file
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        logger.info(f"File saved to {file_path}")

        # Process document
        processor = DocumentProcessor()
        chunks = processor.process_document(file_path)
        logger.info(f"Processed document into {len(chunks)} chunks")

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text could be extracted from this file.",
            )

        # Add to RAG
        from app.main import get_rag_service
        rag_service = get_rag_service()
        
        success = rag_service.add_documents(chunks)
        if success:
            logger.info(f"Document added successfully to ChromaDB")
        else:
            raise HTTPException(status_code=500, detail="Failed to add document to ChromaDB")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "id": file_id,
                "filename": file.filename,
                "size": len(content),
                "chunks": len(chunks),
                "message": "Document uploaded and stored in ChromaDB successfully"
            }
        )

    except Exception as e:
        logger.error(f"Error in upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/summarize")
async def summarize_document(req: SummarizeRequest):
    try:
        from app.main import get_rag_service
        rag_service = get_rag_service()

        query = "Generate a comprehensive summary of the document content."
        logger.info(f"Searching for relevant chunks with query: {query}")
        
        results = rag_service.search(query, k=10)
        logger.info(f"Found {len(results)} relevant chunks")
        
        if not results:
            raise HTTPException(status_code=404, detail="No relevant content found for summarization")
        
        context = "\n\n".join([r["text"] for r in results])
        prompt = f"""Please generate a {req.length} summary of the following document in a {req.style} style:

{context}

Summary:"""

        summary = rag_service.generate(prompt)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "summary": summary,
                "chunks_used": len(results),
                "style": req.style,
                "length": req.length,
                "retrieval_method": "semantic_search"
            }
        )

    except Exception as e:
        logger.error(f"Error in summarize: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")