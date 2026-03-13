"""Markdown file parser."""

import re
import uuid
from pathlib import Path

from app.ingestion.parsers.base import BaseParser
from app.models.internal import Document


class MarkdownParser(BaseParser):
    """Parser for Markdown files.

    Preserves structure while converting to plain text.
    """

    def parse(self, file_path: Path) -> Document:
        """Parse a markdown file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        raw_content = file_path.read_text(encoding="utf-8", errors="ignore")
        stat = file_path.stat()

        # Convert markdown to plain text while preserving structure
        content = self._clean_markdown(raw_content)

        return Document(
            doc_id=str(uuid.uuid4())[:8],
            file_path=str(file_path),
            content=content,
            file_type=".md",
            file_size=stat.st_size,
        )

    def _clean_markdown(self, text: str) -> str:
        """Clean markdown formatting while preserving readability."""
        # Remove code block markers but keep content
        text = re.sub(r"```[\w]*\n?", "\n", text)

        # Convert headers to plain text with separators
        text = re.sub(r"^#{1,6}\s+(.+)$", r"\n\1\n", text, flags=re.MULTILINE)

        # Remove link formatting, keep text
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

        # Remove image markup
        text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"", text)

        # Remove bold/italic markers
        text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
        text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)

        # Remove inline code markers
        text = re.sub(r"`([^`]+)`", r"\1", text)

        # Clean up excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @classmethod
    def supported_extensions(cls) -> list[str]:
        return [".md", ".markdown"]
