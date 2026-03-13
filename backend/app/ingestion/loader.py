"""Document loader for ingesting files from directories."""

from pathlib import Path

from app.config import get_settings
from app.ingestion.parsers import get_parser
from app.models.internal import Document
from app.observability import get_logger
from app.utils.ignore_rules import should_ignore, should_ignore_by_size

logger = get_logger(__name__)


class DocumentLoader:
    """Loads documents from a directory with filtering and parsing."""

    def __init__(self, docs_path: Path | None = None):
        """Initialize the loader.

        Args:
            docs_path: Path to documents directory. Uses config default if not provided.
        """
        settings = get_settings()
        self.docs_path = docs_path or settings.docs_path
        self.loaded_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.errors: list[str] = []

    def load_all(self) -> list[Document]:
        """Load all supported documents from the directory.

        Returns:
            List of parsed Document objects
        """
        documents: list[Document] = []

        if not self.docs_path.exists():
            logger.warning("docs_path_not_found", path=str(self.docs_path))
            return documents

        logger.info("loading_documents", path=str(self.docs_path))

        # Walk the directory tree
        for file_path in self.docs_path.rglob("*"):
            if not file_path.is_file():
                continue

            doc = self._load_file(file_path)
            if doc:
                documents.append(doc)

        logger.info(
            "documents_loaded",
            loaded=self.loaded_count,
            skipped=self.skipped_count,
            errors=self.error_count,
        )

        return documents

    def _load_file(self, file_path: Path) -> Document | None:
        """Load a single file.

        Args:
            file_path: Path to the file

        Returns:
            Document if loaded successfully, None otherwise
        """
        # Check ignore rules
        if should_ignore(file_path, self.docs_path):
            self.skipped_count += 1
            logger.debug("file_ignored", path=str(file_path), reason="pattern")
            return None

        # Check file size
        if should_ignore_by_size(file_path):
            self.skipped_count += 1
            logger.debug("file_ignored", path=str(file_path), reason="size")
            return None

        # Get parser for this file type
        parser_class = get_parser(file_path.suffix)
        if not parser_class:
            self.skipped_count += 1
            logger.debug("file_ignored", path=str(file_path), reason="unsupported_type")
            return None

        # Parse the file
        try:
            parser = parser_class()
            document = parser.parse(file_path)
            self.loaded_count += 1
            logger.debug(
                "file_loaded",
                path=str(file_path),
                size=document.file_size,
                type=document.file_type,
            )
            return document
        except Exception as e:
            self.error_count += 1
            error_msg = f"Failed to parse {file_path}: {e}"
            self.errors.append(error_msg)
            logger.error("file_parse_error", path=str(file_path), error=str(e))
            return None

    def load_file(self, file_path: Path | str) -> Document | None:
        """Load a single file by path.

        Args:
            file_path: Path to the file

        Returns:
            Document if loaded successfully, None otherwise
        """
        path = Path(file_path) if isinstance(file_path, str) else file_path
        return self._load_file(path)
