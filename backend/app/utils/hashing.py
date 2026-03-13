"""Content hashing utilities."""

import hashlib


def hash_content(content: str, length: int = 16) -> str:
    """Generate a SHA256 hash of content.

    Args:
        content: Text content to hash
        length: Number of hex characters to return (max 64)

    Returns:
        Hexadecimal hash string
    """
    full_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return full_hash[:min(length, 64)]


def hash_file(file_path: str) -> str:
    """Generate a SHA256 hash of a file's content.

    Args:
        file_path: Path to the file

    Returns:
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()[:16]
