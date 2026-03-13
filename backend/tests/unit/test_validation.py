"""Unit tests for input validation."""

import pytest

from app.safety.validation import ValidationError, validate_query, validate_top_k


class TestValidateQuery:
    """Tests for query validation."""

    def test_valid_query_passes(self):
        """Valid queries pass validation."""
        result = validate_query("What is the capital of France?")
        assert result == "What is the capital of France?"

    def test_query_trimmed(self):
        """Query whitespace is trimmed."""
        result = validate_query("  test query  ")
        assert result == "test query"

    def test_empty_query_fails(self):
        """Empty queries fail validation."""
        with pytest.raises(ValidationError) as exc:
            validate_query("")
        assert "empty" in exc.value.message.lower()

    def test_whitespace_query_fails(self):
        """Whitespace-only queries fail validation."""
        with pytest.raises(ValidationError):
            validate_query("   ")

    def test_too_short_query_fails(self):
        """Very short queries fail validation."""
        with pytest.raises(ValidationError) as exc:
            validate_query("ab")
        assert "short" in exc.value.message.lower()

    def test_too_long_query_fails(self):
        """Queries exceeding max length fail validation."""
        long_query = "a" * 501
        with pytest.raises(ValidationError) as exc:
            validate_query(long_query)
        assert "exceeds" in exc.value.message.lower()

    def test_control_characters_removed(self):
        """Control characters are removed from query."""
        result = validate_query("test\x00query\x1f")
        assert "\x00" not in result
        assert "\x1f" not in result
        assert "testquery" in result

    def test_excessive_whitespace_normalized(self):
        """Excessive whitespace is normalized."""
        result = validate_query("test    query  here")
        assert result == "test query here"


class TestValidateTopK:
    """Tests for top_k validation."""

    def test_valid_top_k_passes(self):
        """Valid top_k values pass."""
        assert validate_top_k(5) == 5
        assert validate_top_k(1) == 1
        assert validate_top_k(20) == 20

    def test_zero_top_k_fails(self):
        """top_k of 0 fails."""
        with pytest.raises(ValidationError):
            validate_top_k(0)

    def test_negative_top_k_fails(self):
        """Negative top_k fails."""
        with pytest.raises(ValidationError):
            validate_top_k(-1)

    def test_too_large_top_k_fails(self):
        """top_k > 20 fails."""
        with pytest.raises(ValidationError):
            validate_top_k(21)
