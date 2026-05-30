"""Semantic search over the Signal vector database.

Provides hybrid keyword + vector search for the personal knowledge library.
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from src.core.config import SIGNAL_POSTGRES_DSN
from src.vector.db import get_pool
from src.vector.embed import embed_text

logger = logging.getLogger(__name__)


async def search_library(
    query: str,
    owner_id: str,
    mode: Literal["keyword", "vector", "hybrid"] = "hybrid",
    limit: int = 12,
) -> list[dict[str, Any]]:
    """Search library entries by keyword, vector, or hybrid mode.

    Args:
        query: Search query text.
        owner_id: Owner ID to scope results (required, no default).
        mode: "keyword" (store only), "vector" (embedding only), or "hybrid".
        limit: Maximum results to return.

    Returns:
        List of enriched entry dicts with similarity scores when applicable.
    """
    if not query.strip():
        return []

    keyword_results: list[dict[str, Any]] = []

    # --- Keyword search path ---
    if mode in ("keyword", "hybrid"):
        from src.core.libraries import _get_store as _get_library_store
        keyword_results = _get_library_store().search_entries(query, limit=limit)
        if mode == "keyword":
            logger.info(
                "Keyword search: query='%s' mode=%s limit=%d results=%d",
                query, mode, limit, len(keyword_results),
            )
            return keyword_results
        if len(keyword_results) >= limit // 2:
            logger.info(
                "Hybrid search (keyword fast path): query='%s' mode=%s limit=%d results=%d",
                query, mode, limit, len(keyword_results),
            )
            return keyword_results

    # --- Vector search path ---
    if not SIGNAL_POSTGRES_DSN:
        logger.info(
            "Vector search skipped (no DSN): query='%s' mode=%s limit=%d fallback_results=%d",
            query, mode, limit, len(keyword_results),
        )
        return keyword_results if mode == "hybrid" else []

    try:
        vec = embed_text(query, task_type="RETRIEVAL_QUERY")
    except Exception:
        logger.warning("Embedding failed for query '%s', falling back to keyword", query, exc_info=True)
        return keyword_results if mode == "hybrid" else []

    try:
        async with get_pool().connection() as conn:
            rows = await conn.fetchall(
                """
                SELECT entry_id, section, source_url, 1 - (embedding <=> %s::vector) AS similarity
                FROM signal_embeddings
                WHERE owner_id = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (vec, owner_id, vec, limit),
            )
    except Exception:
        logger.warning("Vector DB query failed for '%s', falling back to keyword", query, exc_info=True)
        return keyword_results if mode == "hybrid" else []

    # Enrich vector results with store metadata; skip stale embeddings
    seen_ids = {r.get("id") for r in keyword_results if r.get("id")}
    vector_results: list[dict[str, Any]] = []

    for row in rows:
        entry_id = row.get("entry_id")
        if not entry_id:
            continue
        # Skip duplicates already in keyword results
        if entry_id in seen_ids:
            continue
        from src.core.libraries import _get_store as _get_library_store
        entry = _get_library_store().get_entry(entry_id)
        if entry is None:
            # Stale embedding — entry was deleted since embedding was stored
            continue
        entry["similarity"] = round(float(row.get("similarity", 0.0)), 3)
        vector_results.append(entry)
        seen_ids.add(entry_id)

    # Combine: keyword results first, then vector results
    combined = keyword_results + vector_results
    combined = combined[:limit]

    logger.info(
        "Vector search: query='%s' mode=%s limit=%d keyword=%d vector=%d total=%d",
        query, mode, limit, len(keyword_results), len(vector_results), len(combined),
    )
    return combined
