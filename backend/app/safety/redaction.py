"""PII and profanity redaction stub."""

import re

from app.observability import get_logger

logger = get_logger(__name__)

# Common PII patterns (simplified for stub)
PII_PATTERNS = [
    # Email addresses
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]"),
    # Phone numbers (various formats)
    (r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE]"),
    (r"\b\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE]"),
    # Social Security Numbers
    (r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b", "[SSN]"),
    # Credit card numbers (basic pattern)
    (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[CC]"),
    # IP addresses
    (r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[IP]"),
]

# Basic profanity list (placeholder - would be expanded in production)
PROFANITY_WORDS: set[str] = set()  # Add words as needed


def redact_pii(text: str) -> tuple[str, int]:
    """Redact potential PII from text.

    Args:
        text: Input text

    Returns:
        Tuple of (redacted text, number of redactions)
    """
    redaction_count = 0

    for pattern, replacement in PII_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            redaction_count += len(matches)
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    if redaction_count > 0:
        logger.info("pii_redacted", count=redaction_count)

    return text, redaction_count


def redact_profanity(text: str) -> tuple[str, int]:
    """Redact profanity from text.

    Args:
        text: Input text

    Returns:
        Tuple of (redacted text, number of redactions)
    """
    if not PROFANITY_WORDS:
        return text, 0

    redaction_count = 0
    words = text.split()

    for i, word in enumerate(words):
        clean_word = re.sub(r"[^\w]", "", word.lower())
        if clean_word in PROFANITY_WORDS:
            words[i] = "[REDACTED]"
            redaction_count += 1

    if redaction_count > 0:
        logger.info("profanity_redacted", count=redaction_count)

    return " ".join(words), redaction_count


def redact_content(text: str) -> str:
    """Apply all redaction filters to text.

    Args:
        text: Input text

    Returns:
        Redacted text
    """
    text, pii_count = redact_pii(text)
    text, profanity_count = redact_profanity(text)

    return text
