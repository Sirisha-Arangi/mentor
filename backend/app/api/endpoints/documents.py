# backend/app/api/endpoints/documents.py
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse

from app.services.document_processor import DocumentProcessor
from app.models.document import DocumentChunk
from app.config import settings
from rag_singleton import get_rag_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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
        try:
            content = await file.read()
            logger.info(f"Read {len(content)} bytes from file")

            with open(file_path, "wb") as buffer:
                buffer.write(content)
            logger.info(f"File saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving file: {str(e)}",
            )

        # Process document
        try:
            logger.info("Initializing DocumentProcessor")
            processor = DocumentProcessor()
            logger.info("Processing document...")
            chunks = processor.process_document(file_path)
            logger.info(f"Processed document into {len(chunks)} chunks")

            if not chunks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No text could be extracted from this file. If it's a scanned PDF/image PDF, OCR is required.",
                )

        except HTTPException:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}", exc_info=True)
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing document: {str(e)}",
            )

        # Use RAG service from singleton
        rag_service = get_rag_service()
        logger.info(f"RAG service from singleton: {type(rag_service)}")
        
        # Add to RAG
        try:
            success = rag_service.add_documents(chunks)
            if success:
                logger.info(f"Document added successfully. Total chunks: {len(rag_service.chunks)}")
            else:
                raise HTTPException(status_code=500, detail="Failed to add document")
        except Exception as e:
            logger.error(f"Error adding to vector store: {str(e)}", exc_info=True)
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "id": file_id,
                "filename": file.filename,
                "size": len(content),
                "chunks": len(chunks),
                "message": "Document uploaded successfully"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_document: {str(e)}", exc_info=True)
        if "file_path" in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up file: {str(cleanup_error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post("/summarize")
async def summarize_document(req: SummarizeRequest):
    try:
        # Use RAG service from singleton
        rag_service = get_rag_service()
        logger.info(f"Summarize request - RAG has {len(rag_service.chunks)} chunks")

        query = "Generate a comprehensive summary of the document content."
        logger.info(f"Searching with query: {query}")
        
        results = rag_service.search(query, k=10)
        logger.info(f"Search returned {len(results)} results")
        
        if results:
            logger.info(f"First result text: {results[0].get('text', 'No text')[:100]}...")
        else:
            logger.warning("No search results found!")

        context = "\n\n".join([r["text"] for r in results])
        logger.info(f"Context length: {len(context)} characters")

        prompt = f"""Please generate a {req.length} summary of the following document in a {req.style} style:

{context}

Summary:"""

        summary = rag_service.generate(prompt)
        logger.info(f"Generated summary length: {len(summary)}")

        return {
            "summary": summary,
            "chunks_used": len(results),
            "style": req.style,
            "length": req.length,
        }
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")