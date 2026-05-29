"""Library write hook for real-time embedding indexing."""

from __future__ import annotations

import logging

from src.vector.db import get_pool
from src.vector.embed import content_hash, embed_text

logger = logging.getLogger(__name__)


async def on_entry_saved(
    entry_id: str,
    text: str,
    section: str,
    owner_id: str,
    source_url: str | None = None,
) -> None:
    """Generate an embedding for a library entry and upsert it into signal_embeddings.

    This is a fire-and-forget hook: it is called via ``asyncio.create_task`` after
    a library entry is saved.  Any exception is caught and logged so that embedding
    failures never break library saves.
    """
    try:
        vec = embed_text(text, task_type="RETRIEVAL_DOCUMENT")
        _hash = content_hash(text)

        async with get_pool().connection() as conn:
            await conn.execute(
                """
                INSERT INTO signal_embeddings (
                    owner_id, entry_id, section, content_hash, embedding, source_url
                )
                VALUES (%s, %s, %s, %s, %s::vector, %s)
                ON CONFLICT (owner_id, entry_id) DO UPDATE
                  SET embedding = EXCLUDED.embedding,
                      content_hash = EXCLUDED.content_hash,
                      source_url = EXCLUDED.source_url
                """,
                (owner_id, entry_id, section, _hash, vec, source_url),
            )
            await conn.commit()

        logger.info("Embedding indexed for entry %s (%s).", entry_id, section)
    except Exception:
        logger.warning("Embedding hook failed for entry %s", entry_id, exc_info=True)
