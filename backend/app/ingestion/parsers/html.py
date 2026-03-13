"""HTML file parser using BeautifulSoup."""

import uuid
from pathlib import Path

from bs4 import BeautifulSoup

from app.ingestion.parsers.base import BaseParser
from app.models.internal import Document


class HTMLParser(BaseParser):
    """Parser for HTML files using BeautifulSoup."""

    # Tags to remove entirely
    REMOVE_TAGS = ["script", "style", "nav", "footer", "header", "aside", "noscript"]

    def parse(self, file_path: Path) -> Document:
        """Parse an HTML file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        raw_content = file_path.read_text(encoding="utf-8", errors="ignore")
        stat = file_path.stat()

        # Parse HTML and extract text
        content = self._extract_text(raw_content)

        return Document(
            doc_id=str(uuid.uuid4())[:8],
            file_path=str(file_path),
            content=content,
            file_type=".html",
            file_size=stat.st_size,
        )

    def _extract_text(self, html: str) -> str:
        """Extract text content from HTML."""
        soup = BeautifulSoup(html, "lxml")

        # Remove unwanted tags
        for tag in self.REMOVE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()

        # Get text with proper spacing
        text = soup.get_text(separator="\n", strip=True)

        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n\n".join(lines)

    @classmethod
    def supported_extensions(cls) -> list[str]:
        return [".html", ".htm"]
