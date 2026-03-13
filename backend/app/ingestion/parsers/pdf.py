"""PDF file parser using PyMuPDF."""

import uuid
from pathlib import Path

import fitz  # PyMuPDF

from app.ingestion.parsers.base import BaseParser
from app.models.internal import Document


class PDFParser(BaseParser):
    """Parser for PDF files using PyMuPDF (fitz)."""

    def parse(self, file_path: Path) -> Document:
        """Parse a PDF file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = file_path.stat()
        content = self._extract_text(file_path)

        return Document(
            doc_id=str(uuid.uuid4())[:8],
            file_path=str(file_path),
            content=content,
            file_type=".pdf",
            file_size=stat.st_size,
        )

    def _extract_text(self, file_path: Path) -> str:
        """Extract text from PDF using PyMuPDF."""
        doc = fitz.open(str(file_path))
        text_parts: list[str] = []

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Extract text with proper layout
                text = page.get_text("text")
                if text.strip():
                    text_parts.append(f"[Page {page_num + 1}]\n{text.strip()}")
        finally:
            doc.close()

        return "\n\n".join(text_parts)

    @classmethod
    def supported_extensions(cls) -> list[str]:
        return [".pdf"]
