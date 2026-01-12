from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
import logging
import os
import uuid
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional

from app.services.document_processor import DocumentProcessor
from app.models.document import DocumentChunk
from app.config import settings

router = APIRouter()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add after existing imports
class FlashcardGenerateRequest(BaseModel):
    doc_id: str
    topic: str
    num_cards: int = 10
    difficulty: str = "medium"
    card_types: Optional[List[str]] = ["definition", "concept", "application"]
class SummarizeRequest(BaseModel):
    doc_id: str
    style: str = "concise"
    length: str = "medium"


class TopicSummarizeRequest(BaseModel):
    doc_id: str
    topic: str
    style: str = "concise"
    length: str = "medium"


class QAGenerateRequest(BaseModel):
    doc_id: str
    topic: str
    num_questions: int = 5
    question_types: Optional[List[str]] = ["conceptual", "descriptive"]
    difficulty_levels: Optional[List[str]] = ["easy", "medium"]


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

        # Add to LangChain RAG
        from rag_singleton import get_rag_service
        rag_service = get_rag_service()
        
        success = rag_service.add_documents(chunks)
        if success:
            logger.info(f"Document added successfully to LangChain ChromaDB")
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
        from rag_singleton import get_rag_service
        rag_service = get_rag_service()

        query = "Generate a comprehensive summary of document content."
        logger.info(f"Searching for relevant chunks with query: {query}")
        
        results = rag_service.search(query, k=10)
        logger.info(f"Found {len(results)} relevant chunks")
        
        if not results:
            raise HTTPException(status_code=404, detail="No relevant content found for summarization")
        
        context = "\n\n".join([r["text"] for r in results])
        prompt = f"""Please generate a {req.length} summary of following document in a {req.style} style:

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


@router.post("/topic-summary")
async def generate_topic_summary(req: TopicSummarizeRequest):
    try:
        from rag_singleton import get_rag_service
        rag_service = get_rag_service()

        # Use topic as search query for targeted content retrieval
        query = f"Find information about {req.topic} in document"
        logger.info(f"Searching for topic-specific content: {req.topic}")
        
        results = rag_service.search(query, k=8)
        logger.info(f"Found {len(results)} relevant chunks for topic: {req.topic}")
        
        if not results:
            raise HTTPException(
                status_code=404, 
                detail=f"No relevant content found for topic: {req.topic}"
            )
        
        # Extract topic-specific content
        context = "\n\n".join([r["text"] for r in results])
        
        # Generate focused summary for specific topic
        prompt = f"""Please generate a {req.length} summary focused specifically on "{req.topic}" from the following document content. 
Only summarize information related to {req.topic}. Ignore other topics. Use a {req.style} style.

Document Content:
{context}

Topic-Specific Summary:"""

        summary = rag_service.generate(prompt)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "summary": summary,
                "topic": req.topic,
                "chunks_used": len(results),
                "style": req.style,
                "length": req.length,
                "retrieval_method": "topic_semantic_search"
            }
        )

    except Exception as e:
        logger.error(f"Error in topic summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/generate-qa")
async def generate_qa_pairs(req: QAGenerateRequest):
    try:
        from rag_singleton import get_rag_service
        rag_service = get_rag_service()
        
        # Import Q&A generator
        from app.services.academic.qa_generator import QAGenerator
        qa_generator = QAGenerator(rag_service)
        
        # Generate Q&A pairs
        result = qa_generator.generate_qa_pairs(
            topic=req.topic,
            num_questions=req.num_questions,
            question_types=req.question_types,
            difficulty_levels=req.difficulty_levels
        )
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "qa_pairs": result["qa_pairs"],
                    "topic": req.topic,
                    "total_questions": result["total_questions"],
                    "difficulty_distribution": result["difficulty_distribution"],
                    "topics_covered": result["topics_covered"],
                    "source_chunks_used": result["source_chunks_used"]
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to generate Q&A pairs")
            )
            
    except Exception as e:
        logger.error(f"Error in Q&A generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/generate-flashcards")
async def generate_flashcards(req: FlashcardGenerateRequest):
    try:
        from rag_singleton import get_rag_service
        rag_service = get_rag_service()
        
        # Import flashcard generator
        from app.services.academic.flashcard_generator import FlashcardGenerator
        flashcard_generator = FlashcardGenerator(rag_service)
        
        # Generate flashcards
        result = flashcard_generator.generate_flashcards(
            topic=req.topic,
            num_cards=req.num_cards,
            difficulty=req.difficulty,
            card_types=req.card_types
        )
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "flashcards": result["flashcards"],
                    "topic": req.topic,
                    "total_cards": result["total_cards"],
                    "difficulty_level": result["difficulty_level"],
                    "card_types_used": result["card_types_used"],
                    "source_chunks_used": result["source_chunks_used"]
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to generate flashcards")
            )
            
    except Exception as e:
        logger.error(f"Error in flashcard generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")