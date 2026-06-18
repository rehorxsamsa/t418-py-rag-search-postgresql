"""Embedding generation.

Abstracted behind an interface so the provider can be swapped (local model,
Voyage AI, OpenAI, etc.) without touching the rest of the app. The demo
defaults to a local sentence-transformers model so it runs with zero API keys.
"""

from abc import ABC, abstractmethod
from functools import lru_cache

from app.config import settings


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...


class LocalEmbeddingProvider(EmbeddingProvider):
    """Runs all-MiniLM-L6-v2 locally (384-dim). No external calls."""

    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    """Factory + singleton. Extend here to add cloud providers."""
    if settings.embedding_provider == "local":
        return LocalEmbeddingProvider()
    raise ValueError(f"Unknown embedding provider: {settings.embedding_provider}")
