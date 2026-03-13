"""Base parser interface for document loading."""

from abc import ABC, abstractmethod
from pathlib import Path

from app.models.internal import Document


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, file_path: Path) -> Document:
        """Parse a file and return a Document.

        Args:
            file_path: Path to the file to parse

        Returns:
            Document with content extracted from the file

        Raises:
            ValueError: If the file cannot be parsed
            FileNotFoundError: If the file doesn't exist
        """
        pass

    @classmethod
    def supported_extensions(cls) -> list[str]:
        """Return list of supported file extensions."""
        return []
