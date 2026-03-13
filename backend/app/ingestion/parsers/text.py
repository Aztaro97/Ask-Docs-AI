"""Plain text file parser."""

import uuid
from pathlib import Path

from app.ingestion.parsers.base import BaseParser
from app.models.internal import Document


class TextParser(BaseParser):
    """Parser for plain text files."""

    def parse(self, file_path: Path) -> Document:
        """Parse a text file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file_path.read_text(encoding="utf-8", errors="ignore")
        stat = file_path.stat()

        return Document(
            doc_id=str(uuid.uuid4())[:8],
            file_path=str(file_path),
            content=content,
            file_type=".txt",
            file_size=stat.st_size,
        )

    @classmethod
    def supported_extensions(cls) -> list[str]:
        return [".txt"]
