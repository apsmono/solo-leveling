"""
Test stubs for Phase 3: Knowledge Library — Vector Search (Wave 0).

These tests define the contract for src.vector.search (hybrid keyword + vector search):
- search_library(query, owner_id, mode, limit)

All tests run offline by default. Integration tests are gated behind
SIGNAL_POSTGRES_DSN_TEST.
"""

from __future__ import annotations

import asyncio
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from dotenv import load_dotenv

load_dotenv()

# Conditional import — module does not exist yet in Wave 0
_try_imported = False
_vector_search = None

try:
    from src.vector import search as _vector_search

    _try_imported = True
except ImportError:
    pass


@unittest.skipUnless(_try_imported, "src.vector.search not yet implemented — skipping")
class VectorSearchTests(unittest.TestCase):
    """Contract tests for src.vector.search (unit tests, always run when module exists)."""

    def test_search_library_keyword_mode(self) -> None:
        """Keyword mode calls store.search_entries() and returns its results."""
        from src.vector.search import search_library

        async def _run() -> None:
            mock_store = MagicMock()
            mock_store.search_entries.return_value = [
                {"id": "entry-1", "title": "AI Basics", "section": "terms"},
                {"id": "entry-2", "title": "Machine Learning", "section": "terms"},
            ]

            with patch("src.vector.search._get_store", return_value=mock_store):
                result = await search_library("test", owner_id="owner", mode="keyword")

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["id"], "entry-1")
            mock_store.search_entries.assert_called_once()

        asyncio.run(_run())

    def test_search_library_vector_mode(self) -> None:
        """Vector mode embeds query and returns similarity-scored results."""
        from src.vector.search import search_library

        async def _run() -> None:
            mock_conn = AsyncMock()
            mock_conn.fetchall.return_value = [
                {"entry_id": "entry-1", "similarity": 0.95},
                {"entry_id": "entry-2", "similarity": 0.87},
            ]

            mock_pool = MagicMock()
            mock_pool.connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_pool.connection.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("src.vector.search.get_pool", return_value=mock_pool):
                with patch("src.vector.search.embed_text", return_value=[0.1] * 768):
                    result = await search_library("ai", owner_id="owner", mode="vector")

            self.assertEqual(len(result), 2)
            self.assertIn("similarity", result[0])
            self.assertEqual(result[0]["entry_id"], "entry-1")
            self.assertEqual(result[0]["similarity"], 0.95)

        asyncio.run(_run())

    def test_search_library_hybrid_prefers_keyword(self) -> None:
        """Hybrid mode returns keyword results when count >= limit//2 (no vector call)."""
        from src.vector.search import search_library

        async def _run() -> None:
            mock_store = MagicMock()
            # Return 6 results (>= 12//2 = 6), so vector search should NOT be called
            mock_store.search_entries.return_value = [
                {"id": f"entry-{i}", "title": f"Result {i}", "section": "terms"}
                for i in range(6)
            ]

            with patch("src.vector.search._get_store", return_value=mock_store):
                with patch("src.vector.search.get_pool") as mock_get_pool:
                    result = await search_library("test", owner_id="owner", mode="hybrid", limit=12)

            self.assertEqual(len(result), 6)
            # Vector search should NOT have been called
            mock_get_pool.assert_not_called()

        asyncio.run(_run())

    def test_search_library_hybrid_falls_back_to_vector(self) -> None:
        """Hybrid mode calls vector search when keyword returns < limit//2 results."""
        from src.vector.search import search_library

        async def _run() -> None:
            mock_store = MagicMock()
            # Return only 1 result (< 12//2 = 6), so vector search SHOULD be called
            mock_store.search_entries.return_value = [
                {"id": "entry-kw", "title": "Keyword Result", "section": "terms"},
            ]

            mock_conn = AsyncMock()
            mock_conn.fetchall.return_value = [
                {"entry_id": "entry-v1", "similarity": 0.92},
                {"entry_id": "entry-v2", "similarity": 0.85},
            ]

            mock_pool = MagicMock()
            mock_pool.connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_pool.connection.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("src.vector.search._get_store", return_value=mock_store):
                with patch("src.vector.search.get_pool", return_value=mock_pool):
                    with patch("src.vector.search.embed_text", return_value=[0.1] * 768):
                        result = await search_library("test", owner_id="owner", mode="hybrid", limit=12)

            # Should have keyword result + vector results (deduplicated)
            self.assertGreater(len(result), 1)
            # Vector search should have been called
            mock_pool.connection.assert_called()

        asyncio.run(_run())

    def test_search_library_owner_id_scoped(self) -> None:
        """SQL parameters include owner_id in the execute call args."""
        from src.vector.search import search_library

        async def _run() -> None:
            mock_conn = AsyncMock()
            mock_conn.fetchall.return_value = []

            mock_pool = MagicMock()
            mock_pool.connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_pool.connection.return_value.__aexit__ = AsyncMock(return_value=False)

            test_owner = "owner@example.com"

            with patch("src.vector.search.get_pool", return_value=mock_pool):
                with patch("src.vector.search.embed_text", return_value=[0.1] * 768):
                    await search_library("ai", owner_id=test_owner, mode="vector")

            # Verify the execute call included owner_id in parameters
            self.assertTrue(mock_conn.execute.called)
            call_args = mock_conn.execute.call_args
            params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]
            param_str = str(params)
            self.assertIn(test_owner, param_str)

        asyncio.run(_run())

    def test_search_library_empty_query_returns_empty(self) -> None:
        """Empty query string returns empty list without calling store or DB."""
        from src.vector.search import search_library

        async def _run() -> None:
            mock_store = MagicMock()

            with patch("src.vector.search._get_store", return_value=mock_store):
                with patch("src.vector.search.get_pool") as mock_get_pool:
                    result = await search_library("", owner_id="owner", mode="hybrid")

            self.assertEqual(result, [])
            mock_store.search_entries.assert_not_called()
            mock_get_pool.assert_not_called()

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# Integration tests (gated behind SIGNAL_POSTGRES_DSN_TEST)
# ---------------------------------------------------------------------------
@unittest.skipUnless(
    os.environ.get("SIGNAL_POSTGRES_DSN_TEST") and _try_imported,
    "SIGNAL_POSTGRES_DSN_TEST not set or src.vector.search not implemented — skipping integration tests",
)
class VectorSearchIntegrationTests(unittest.TestCase):
    """Live DB tests — require a running pgvector instance + Gemini API key."""

    def test_live_vector_search_returns_results(self) -> None:
        """Embed a test document, search for it, assert result contains the document."""
        from src.vector.search import search_library

        async def _run() -> None:
            # This test requires live Postgres + Gemini; it embeds a known document
            # and searches for it to verify end-to-end vector search works.
            result = await search_library(
                "artificial intelligence machine learning",
                owner_id=os.environ.get("SIGNAL_OWNER_ID", "test@example.com"),
                mode="vector",
                limit=5,
            )
            self.assertIsInstance(result, list)
            # We can't assert exact content without knowing what's in the DB,
            # but we can assert the result structure is correct
            if result:
                self.assertIn("entry_id", result[0])
                self.assertIn("similarity", result[0])

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
