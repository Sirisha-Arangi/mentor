import os
from typing import List, Dict, Optional
from pydantic import BaseModel
from PyPDF2 import PdfReader
import docx
from pathlib import Path
from datetime import datetime
import re

class DocumentMetadata(BaseModel):
    title: str
    author: Optional[str] = None
    page_number: Optional[int] = None
    section: Optional[str] = None
    created_at: str = datetime.utcnow().isoformat()
    document_id: str

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.section_pattern = re.compile(r'^(#+)\s+(.*)$', re.MULTILINE)

    async def process_document(self, file_path: str, document_id: str) -> List[Dict]:
        """Process document and return chunks with metadata"""
        file_type = self._get_file_type(file_path)
        text = await self._extract_text(file_path, file_type)
        sections = self._split_into_sections(text)
        return self._create_chunks(sections, document_id)

    def _get_file_type(self, file_path: str) -> str:
        """Determine file type from extension"""
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext == '.docx':
            return 'docx'
        elif ext == '.txt':
            return 'txt'
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    async def _extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text based on file type"""
        if file_type == 'pdf':
            return self._extract_from_pdf(file_path)
        elif file_type == 'docx':
            return self._extract_from_docx(file_path)
        elif file_type == 'txt':
            return self._extract_from_txt(file_path)

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF with section detection"""
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page_num, page in enumerate(reader.pages, 1):
                text += f"\n# Page {page_num}\n{page.extract_text()}\n"
            return text

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX with section detection"""
        doc = docx.Document(file_path)
        text = []
        for para in doc.paragraphs:
            if para.style.name.startswith('Heading'):
                level = len(para.style.name.split()[-1])
                text.append(f"{'#' * level} {para.text}")
            else:
                text.append(para.text)
        return "\n".join(text)

    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _split_into_sections(self, text: str) -> List[Dict]:
        """Split text into sections based on markdown headers"""
        sections = []
        current_section = []
        current_level = 1
        current_title = "Document"

        for line in text.split('\n'):
            header_match = self.section_pattern.match(line)
            if header_match:
                if current_section:
                    sections.append({
                        'title': current_title,
                        'level': current_level,
                        'content': '\n'.join(current_section).strip()
                    })
                current_level = len(header_match.group(1))
                current_title = header_match.group(2).strip()
                current_section = []
            else:
                current_section.append(line)

        if current_section:
            sections.append({
                'title': current_title,
                'level': current_level,
                'content': '\n'.join(current_section).strip()
            })

        return sections

    def _create_chunks(
        self,
        sections: List[Dict],
        document_id: str
    ) -> List[Dict]:
        """Create chunks from document sections"""
        chunks = []
        chunk_id = 0

        for section in sections:
            text = f"# {section['title']}\n{section['content']}"
            words = text.split()
            
            for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
                chunk_words = words[i:i + self.chunk_size]
                chunk_text = ' '.join(chunk_words)
                
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'document_id': document_id,
                        'section': section['title'],
                        'chunk_id': f"{document_id}_{chunk_id}",
                        'section_level': section['level']
                    }
                })
                chunk_id += 1

        return chunks