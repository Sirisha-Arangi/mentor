# backend/app/models/document.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class DocumentChunk(BaseModel):
    text: str
    document_id: str
    metadata: Optional[Dict[str, Any]] = None

class Document(BaseModel):
    id: str
    filename: str
    chunks: List[DocumentChunk]
    metadata: Dict[str, Any] = {}