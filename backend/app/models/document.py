# backend/app/models/document.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

class DocumentType(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    document_type: DocumentType
    file_path: str
    file_size: int
    page_count: Optional[int] = None
    metadata: dict = Field(default_factory=dict)

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True