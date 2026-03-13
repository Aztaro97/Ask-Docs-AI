"""Application configuration using pydantic-settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Paths
    docs_path: Path = Field(default=Path("./docs"))
    index_path: Path = Field(default=Path("./data/index"))
    cache_path: Path = Field(default=Path("./data/cache"))

    # Document processing
    max_file_size_mb: int = 50
    max_chunks_per_doc: int = 1000
    chunk_size: int = 512  # tokens
    chunk_overlap: int = 64  # tokens

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_batch_size: int = 32
    embedding_cache_size: int = 10000

    # Reranking
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    rerank_top_k: int = 10  # Retrieve more, rerank to top_k

    # Retrieval
    top_k: int = 5
    min_relevance_score: float = 0.2  # Lowered to allow more matches
    min_citations: int = 1

    # LLM
    llm_provider: Literal["ollama", "llama_cpp"] = "ollama"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    llama_cpp_model_path: str = ""
    llm_max_tokens: int = 1024
    llm_temperature: float = 0.7

    # Rate limiting
    rate_limit_rpm: int = 60

    # Query
    max_query_length: int = 500

    # Ignore patterns
    ignore_patterns: list[str] = Field(
        default=[
            ".env",
            ".env.*",
            "node_modules",
            ".git",
            "__pycache__",
            "*.pyc",
            ".DS_Store",
            "*.log",
        ]
    )

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
