"""Gemini embedding client for the Signal vector database."""

from __future__ import annotations

import hashlib
import logging
import os
from typing import Literal

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

_EMBED_MODEL = "gemini-embedding-001"
_EMBED_DIM = 768
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """Lazy singleton for the Gemini embedding client."""
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY is not set.")
        _client = genai.Client(api_key=api_key)
    return _client


def embed_text(
    text: str,
    task_type: Literal["RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"] = "RETRIEVAL_DOCUMENT",
) -> list[float]:
    """Generate a 768-dim embedding vector for the given text via Gemini.

    Args:
        text: The text to embed.
        task_type: Gemini task type — RETRIEVAL_DOCUMENT for content,
            RETRIEVAL_QUERY for search queries.

    Returns:
        A list of 768 floats representing the embedding vector.
    """
    result = _get_client().models.embed_content(
        model=_EMBED_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=_EMBED_DIM,
        ),
    )
    values = result.embeddings[0].values
    logger.info("Embedded text (%d chars) -> %d-dim vector.", len(text), len(values))
    return values


def content_hash(text: str) -> str:
    """Return the SHA-256 hex digest of *text* (UTF-8)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
