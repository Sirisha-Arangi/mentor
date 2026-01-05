# backend/app/services/document_processor.py
import os
import logging
from typing import List
from pathlib import Path

from app.models.document import DocumentChunk

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(
            f"Initialized DocumentProcessor with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )

    def process_document(self, file_path: str) -> List[DocumentChunk]:
        try:
            logger.info(f"Processing document: {file_path}")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            file_ext = Path(file_path).suffix.lower()
            logger.info(f"Detected file extension: {file_ext}")

            if file_ext == ".txt":
                text = self._read_txt(file_path)
            elif file_ext == ".pdf":
                text = self._read_pdf(file_path)
            elif file_ext in [".doc", ".docx"]:
                text = self._read_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

            logger.info(f"Read {len(text)} characters from {file_path}")

            chunks = self._split_into_chunks(text)
            logger.info(f"Split document into {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}", exc_info=True)
            raise

    def _read_txt(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _read_pdf(self, file_path: str) -> str:
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(file_path)
            text = ""

            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"

            return text

        except ImportError:
            logger.error("PyPDF2 is required for PDF processing. Install with: pip install pypdf2")
            raise

    def _read_docx(self, file_path: str) -> str:
        try:
            from docx import Document

            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])

        except ImportError:
            logger.error("python-docx is required for DOCX processing. Install with: pip install python-docx")
            raise

    def _split_into_chunks(self, text: str) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        start = 0
        doc_id = str(hash(text))

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        text=chunk_text,
                        document_id=doc_id,
                        metadata={
                            "chunk_index": len(chunks),
                            "start_pos": start,
                            "end_pos": end,
                        },
                    )
                )

            next_start = end - self.chunk_overlap
            start = next_start if next_start > start else end

        return chunks