"""Document parsers for different file types."""

from app.ingestion.parsers.base import BaseParser
from app.ingestion.parsers.excel import ExcelParser
from app.ingestion.parsers.html import HTMLParser
from app.ingestion.parsers.markdown import MarkdownParser
from app.ingestion.parsers.pdf import PDFParser
from app.ingestion.parsers.text import TextParser

PARSERS: dict[str, type[BaseParser]] = {
    ".md": MarkdownParser,
    ".txt": TextParser,
    ".html": HTMLParser,
    ".htm": HTMLParser,
    ".pdf": PDFParser,
    ".xlsx": ExcelParser,
    ".xls": ExcelParser,
}


def get_parser(file_extension: str) -> type[BaseParser] | None:
    """Get the appropriate parser for a file extension."""
    return PARSERS.get(file_extension.lower())


__all__ = [
    "BaseParser",
    "MarkdownParser",
    "TextParser",
    "HTMLParser",
    "PDFParser",
    "ExcelParser",
    "PARSERS",
    "get_parser",
]
