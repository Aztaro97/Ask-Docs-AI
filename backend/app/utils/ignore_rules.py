"""File ignore rules for document ingestion."""

import fnmatch
from pathlib import Path

from app.config import get_settings

# Default patterns to always ignore
DEFAULT_IGNORE_PATTERNS = [
    # Environment files
    ".env",
    ".env.*",
    "*.env",
    # Version control
    ".git",
    ".git/**",
    ".gitignore",
    ".gitattributes",
    # Dependencies
    "node_modules",
    "node_modules/**",
    "__pycache__",
    "__pycache__/**",
    "*.pyc",
    ".venv",
    "venv",
    # Build artifacts
    "dist",
    "build",
    "*.egg-info",
    # IDE
    ".idea",
    ".vscode",
    "*.swp",
    # OS files
    ".DS_Store",
    "Thumbs.db",
    # Logs
    "*.log",
    "logs/**",
    # Large binary files
    "*.zip",
    "*.tar",
    "*.gz",
    "*.rar",
    "*.7z",
    "*.exe",
    "*.dll",
    "*.so",
    "*.dylib",
    "*.bin",
    # Images (usually not useful for text RAG)
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.svg",
    "*.ico",
    # Other
    "*.lock",
    "package-lock.json",
    "yarn.lock",
]


def should_ignore(file_path: Path, base_path: Path | None = None) -> bool:
    """Check if a file should be ignored based on patterns.

    Args:
        file_path: Path to check
        base_path: Base path for relative matching (optional)

    Returns:
        True if the file should be ignored
    """
    settings = get_settings()

    # Combine default and custom patterns
    patterns = DEFAULT_IGNORE_PATTERNS + settings.ignore_patterns

    # Get relative path for pattern matching
    if base_path:
        try:
            rel_path = file_path.relative_to(base_path)
            path_str = str(rel_path)
        except ValueError:
            path_str = str(file_path)
    else:
        path_str = str(file_path)

    # Check file name and full path against patterns
    file_name = file_path.name

    for pattern in patterns:
        # Check file name
        if fnmatch.fnmatch(file_name, pattern):
            return True
        # Check full path
        if fnmatch.fnmatch(path_str, pattern):
            return True
        # Check if any path component matches
        for part in file_path.parts:
            if fnmatch.fnmatch(part, pattern):
                return True

    return False


def should_ignore_by_size(file_path: Path) -> bool:
    """Check if a file should be ignored due to size."""
    settings = get_settings()
    try:
        size = file_path.stat().st_size
        return size > settings.max_file_size_bytes
    except OSError:
        return True
