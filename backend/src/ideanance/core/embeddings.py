"""OpenAI embedding client wrapper with caching."""

from __future__ import annotations

from typing import Any

EMBEDDING_DIMENSION = 1536  # text-embedding-3-small output dimensions


class EmbeddingClient:
    """Wraps OpenAI's embedding API with an in-memory cache.

    For production: uses text-embedding-3-small (1536 dims).
    For testing: accepts a mock that returns dummy embeddings.
    """

    def __init__(
        self,
        api_key: str = "",
        model: str = "text-embedding-3-small",
        client: Any | None = None,
    ) -> None:
        self.model = model
        self._cache: dict[str, list[float]] = {}
        if client is not None:
            self._client = client
        elif api_key:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=api_key)
        else:
            self._client = None

    async def embed(self, text: str) -> list[float]:
        """Embed a single text. Returns cached if available."""
        if text in self._cache:
            return self._cache[text]
        if self._client is None:
            return self._dummy_embedding()
        response = await self._client.embeddings.create(
            input=[text], model=self.model
        )
        embedding = response.data[0].embedding
        self._cache[text] = embedding
        return embedding

    async def embed_batch(
        self, texts: list[str]
    ) -> list[list[float]]:
        """Embed multiple texts in one API call."""
        if self._client is None:
            return [self._dummy_embedding() for _ in texts]
        response = await self._client.embeddings.create(
            input=texts, model=self.model
        )
        embeddings = [d.embedding for d in response.data]
        for text, emb in zip(texts, embeddings, strict=True):
            self._cache[text] = emb
        return embeddings

    def _dummy_embedding(self) -> list[float]:
        """Return a zero vector for testing without API keys."""
        return [0.0] * EMBEDDING_DIMENSION
