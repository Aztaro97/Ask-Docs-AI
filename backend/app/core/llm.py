"""LLM abstraction for Ollama and llama-cpp-python."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.config import get_settings
from app.observability import get_logger

logger = get_logger(__name__)


class BaseLLM(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a complete response."""
        pass

    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        """Generate response as a stream of tokens."""
        pass


class OllamaLLM(BaseLLM):
    """Ollama LLM provider."""

    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ):
        """Initialize Ollama client.

        Args:
            host: Ollama server URL
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        """
        settings = get_settings()
        self.host = host or settings.ollama_host
        self.model = model or settings.ollama_model
        self.max_tokens = max_tokens or settings.llm_max_tokens
        self.temperature = temperature or settings.llm_temperature
        self.client = httpx.AsyncClient(timeout=120.0)

        logger.info(
            "ollama_initialized",
            host=self.host,
            model=self.model,
        )

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a complete response."""
        response = await self.client.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": kwargs.get("max_tokens", self.max_tokens),
                    "temperature": kwargs.get("temperature", self.temperature),
                },
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        """Generate response as a stream of tokens."""
        async with self.client.stream(
            "POST",
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "num_predict": kwargs.get("max_tokens", self.max_tokens),
                    "temperature": kwargs.get("temperature", self.temperature),
                },
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    import json

                    data = json.loads(line)
                    if token := data.get("response"):
                        yield token
                    if data.get("done"):
                        break

    async def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = await self.client.get(f"{self.host}/api/tags")
            return response.status_code == 200
        except Exception:
            return False


class LlamaCppLLM(BaseLLM):
    """llama-cpp-python LLM provider (fallback)."""

    def __init__(
        self,
        model_path: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ):
        """Initialize llama-cpp-python.

        Args:
            model_path: Path to GGUF model file
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        """
        settings = get_settings()
        self.model_path = model_path or settings.llama_cpp_model_path
        self.max_tokens = max_tokens or settings.llm_max_tokens
        self.temperature = temperature or settings.llm_temperature
        self._llm = None

        if not self.model_path:
            logger.warning("llama_cpp_no_model_path")

    def _get_llm(self):
        """Lazy load the llama-cpp model."""
        if self._llm is None and self.model_path:
            from llama_cpp import Llama

            logger.info("loading_llama_cpp_model", path=self.model_path)
            self._llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,
                n_threads=4,
                verbose=False,
            )
            logger.info("llama_cpp_model_loaded")
        return self._llm

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a complete response."""
        llm = self._get_llm()
        if not llm:
            raise RuntimeError("llama-cpp model not configured")

        output = llm(
            prompt,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            temperature=kwargs.get("temperature", self.temperature),
            stop=["</s>", "\n\n\n"],
        )
        return output["choices"][0]["text"]

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        """Generate response as a stream of tokens."""
        llm = self._get_llm()
        if not llm:
            raise RuntimeError("llama-cpp model not configured")

        for output in llm(
            prompt,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            temperature=kwargs.get("temperature", self.temperature),
            stop=["</s>", "\n\n\n"],
            stream=True,
        ):
            if token := output["choices"][0].get("text"):
                yield token


# Singleton instances
_ollama: OllamaLLM | None = None
_llama_cpp: LlamaCppLLM | None = None


async def get_llm() -> BaseLLM:
    """Get the appropriate LLM instance based on configuration.

    Tries Ollama first, falls back to llama-cpp-python.
    """
    global _ollama, _llama_cpp
    settings = get_settings()

    if settings.llm_provider == "ollama":
        if _ollama is None:
            _ollama = OllamaLLM()

        # Check if Ollama is available
        if await _ollama.is_available():
            return _ollama

        logger.warning("ollama_not_available", falling_back="llama_cpp")

    # Fallback to llama-cpp
    if _llama_cpp is None:
        _llama_cpp = LlamaCppLLM()

    return _llama_cpp
