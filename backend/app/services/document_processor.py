# backend/app/services/document_processor.py
import os
from typing import List, Dict, Optional
from PyPDF2 import PdfReader
import docx
from pathlib import Path

class DocumentProcessor:
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """Extract text from different file types."""
        if file_type == 'pdf':
            return DocumentProcessor._extract_from_pdf(file_path)
        elif file_type == 'docx':
            return DocumentProcessor._extract_from_docx(file_path)
        elif file_type == 'txt':
            return DocumentProcessor._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF file."""
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text = '\n'.join(page.extract_text() for page in reader.pages)
            return text

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = docx.Document(file_path)
        return '\n'.join(paragraph.text for paragraph in doc.paragraphs)

    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """Extract text from TXT file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # TODO: Add more cleaning steps as needed
        return text

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[Dict]:
        """Split text into overlapping chunks with metadata."""
        if not text:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append({
                    'text': chunk,
                    'start': start,
                    'end': end,
                    'length': len(chunk)
                })
            start = end - overlap  # Overlap chunks

        return chunks