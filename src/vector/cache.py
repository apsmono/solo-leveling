"""Token-cache lookup and store for near-duplicate content deduplication."""

from __future__ import annotations

import logging
import os

from src.vector.db import get_pool
from src.vector.embed import content_hash, embed_text

logger = logging.getLogger(__name__)

_COSINE_THRESHOLD: float = float(os.environ.get("SIGNAL_COSINE_THRESHOLD", "0.08"))
_DEFAULT_OWNER: str = os.environ.get("SIGNAL_OWNER_ID", "default-owner")


async def check_cache(text: str, owner_id: str = _DEFAULT_OWNER) -> str | None:
    """Return a cached summary if *text* is near-duplicate of a prior entry.

    Uses cosine distance on 768-dim embeddings.  A hit is logged at INFO level.

    Args:
        text: The input text to check.
        owner_id: Tenant-scoped owner ID.

    Returns:
        The cached summary string, or ``None`` if no near-duplicate exists.
    """
    vec = embed_text(text, task_type="RETRIEVAL_QUERY")

    async with get_pool().connection() as conn:
        row = await conn.fetchone(
            """
            SELECT summary, 1 - (embedding <=> %s::vector) AS similarity
            FROM signal_token_cache
            WHERE owner_id = %s
              AND (embedding <=> %s::vector) < %s
            ORDER BY embedding <=> %s::vector
            LIMIT 1
            """,
            (vec, owner_id, vec, _COSINE_THRESHOLD, vec),
        )

    if row:
        logger.info("Token cache HIT (similarity=%.3f)", row["similarity"])
        return row["summary"]
    return None


async def store_cache(
    text: str, summary: str, owner_id: str = _DEFAULT_OWNER
) -> None:
    """Store *text* + *summary* in the token cache for future deduplication.

    This is best-effort: any exception is caught, logged, and swallowed so that
    cache write failures never break upstream callers.

    Args:
        text: The original text (used for embedding + content hash).
        summary: The generated summary to cache.
        owner_id: Tenant-scoped owner ID.
    """
    try:
        vec = embed_text(text, task_type="RETRIEVAL_DOCUMENT")
        _hash = content_hash(text)

        async with get_pool().connection() as conn:
            await conn.execute(
                """
                INSERT INTO signal_token_cache (
                    owner_id, content_hash, embedding, summary
                )
                VALUES (%s, %s, %s::vector, %s)
                ON CONFLICT (owner_id, content_hash) DO UPDATE
                  SET summary = EXCLUDED.summary,
                      hit_count = signal_token_cache.hit_count + 1
                """,
                (owner_id, _hash, vec, summary),
            )
            await conn.commit()

        logger.info("Token cache stored (hash=%s...).", _hash[:16])
    except Exception:
        logger.warning("Token cache write failed", exc_info=True)
