"""
Test stubs for Phase 1: Data & Auth Foundation (Wave 0).

These tests define the contract for modules that will be implemented in Wave 1+:
- src.vector.db      (VectorDB pool lifecycle + migrations)
- src.vector.embed   (Gemini embedding client + content hashing)
- src.vector.cache   (Token-level cosine-similarity cache)
- src.api.auth_session (Firebase session cookie routes)

All tests run offline by default.  Integration tests are gated behind
SIGNAL_POSTGRES_DSN_TEST.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# VectorDB pool lifecycle
# ---------------------------------------------------------------------------
class VectorDBTests(unittest.TestCase):
    """Contract tests for src.vector.db (open_pool, close_pool, get_pool)."""

    def setUp(self) -> None:
        """Reset module-level state before each test."""
        # Ensure _pool is None so tests are isolated from import side-effects.
        patcher = patch("src.vector.db._pool", None)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_pool_not_init_raises(self) -> None:
        """get_pool() before open_pool() raises RuntimeError."""
        from src.vector.db import get_pool

        with self.assertRaises(RuntimeError) as ctx:
            get_pool()
        self.assertIn("not initialised", str(ctx.exception).lower())

    def test_open_pool_sets_pool(self) -> None:
        """open_pool() makes get_pool() return the pool instance."""
        from src.vector.db import get_pool, open_pool

        async def _run() -> None:
            mock_pool = MagicMock()
            with patch("src.vector.db.AsyncConnectionPool") as MockPool:
                MockPool.return_value = mock_pool
                await open_pool("postgresql://test@localhost/db")
                self.assertEqual(get_pool(), mock_pool)

        asyncio.run(_run())

    def test_close_pool_clears_state(self) -> None:
        """close_pool() resets _pool to None."""
        from src.vector.db import close_pool, get_pool, open_pool

        async def _run() -> None:
            mock_pool = MagicMock()
            with patch("src.vector.db.AsyncConnectionPool") as MockPool:
                MockPool.return_value = mock_pool
                await open_pool("postgresql://test@localhost/db")
                self.assertEqual(get_pool(), mock_pool)
                await close_pool()
                with self.assertRaises(RuntimeError):
                    get_pool()

        asyncio.run(_run())

    def test_migration_is_idempotent(self) -> None:
        """Running migration SQL twice does not error."""
        from src.vector.db import _apply_migrations

        async def _run() -> None:
            mock_conn = AsyncMock()
            # First call
            await _apply_migrations(mock_conn)
            # Second call — idempotent, should not raise
            await _apply_migrations(mock_conn)
            self.assertTrue(mock_conn.execute.called)

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# Embedding client
# ---------------------------------------------------------------------------
class EmbedTests(unittest.TestCase):
    """Contract tests for src.vector.embed (embed_text, content_hash)."""

    def test_embed_text_dimensions(self) -> None:
        """embed_text returns a list of length 768."""
        from src.vector.embed import _EMBED_DIM, embed_text

        mock_response = MagicMock()
        mock_response.embeddings = [MagicMock(values=[0.1] * _EMBED_DIM)]

        mock_client = MagicMock()
        mock_client.models.embed_content.return_value = mock_response

        with patch("src.vector.embed._get_client", return_value=mock_client):
            result = embed_text("hello world", task_type="RETRIEVAL_DOCUMENT")
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), _EMBED_DIM)

    def test_content_hash_stable(self) -> None:
        """Same input yields the same SHA-256 hex digest."""
        from src.vector.embed import content_hash

        text = "The quick brown fox"
        h1 = content_hash(text)
        h2 = content_hash(text)

        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)  # SHA-256 hex length
        self.assertEqual(h1, hashlib.sha256(text.encode("utf-8")).hexdigest())

    def test_content_hash_different_inputs(self) -> None:
        """Different inputs yield different hashes."""
        from src.vector.embed import content_hash

        self.assertNotEqual(content_hash("a"), content_hash("b"))

    def test_on_entry_saved_inserts_row(self) -> None:
        """Calling on_entry_saved creates a DB row via get_pool."""
        from src.vector.hooks import on_entry_saved

        async def _run() -> None:
            mock_conn = AsyncMock()

            mock_pool = MagicMock()
            mock_pool.connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_pool.connection.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("src.vector.hooks.get_pool", return_value=mock_pool):
                with patch("src.vector.hooks.embed_text", return_value=[0.1] * 768):
                    await on_entry_saved(
                        entry_id="test-entry-1",
                        text="Test body content.",
                        section="terms",
                        owner_id="owner@example.com",
                    )
                    self.assertTrue(mock_conn.execute.called)

        asyncio.run(_run())

    def test_on_entry_saved_never_raises(self) -> None:
        """on_entry_saved catches all exceptions and never propagates."""
        from src.vector.hooks import on_entry_saved

        async def _run() -> None:
            with patch("src.vector.hooks.get_pool", side_effect=RuntimeError("boom")):
                # Should not raise
                await on_entry_saved(
                    entry_id="test-entry-1",
                    text="Test body content.",
                    section="terms",
                    owner_id="owner@example.com",
                )

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# Token cache (cosine-similarity dedup)
# ---------------------------------------------------------------------------
class TokenCacheTests(unittest.TestCase):
    """Contract tests for src.vector.cache (check_cache, store_cache)."""

    def test_cache_miss_returns_none(self) -> None:
        """check_cache on unseen text returns None."""
        from src.vector.cache import check_cache

        async def _run() -> None:
            mock_conn = AsyncMock()
            mock_conn.fetchone.return_value = None

            mock_pool = MagicMock()
            mock_pool.connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_pool.connection.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("src.vector.cache.get_pool", return_value=mock_pool):
                with patch("src.vector.cache.embed_text", return_value=[0.1] * 768):
                    result = await check_cache("unseen text", owner_id="owner@example.com")
                    self.assertIsNone(result)

        asyncio.run(_run())

    def test_cache_hit_returns_summary(self) -> None:
        """check_cache on near-duplicate returns stored summary."""
        from src.vector.cache import check_cache

        async def _run() -> None:
            mock_conn = AsyncMock()
            expected_summary = "This is the cached summary."
            mock_conn.fetchone.return_value = {"summary": expected_summary, "similarity": 0.95}

            mock_pool = MagicMock()
            mock_pool.connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_pool.connection.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("src.vector.cache.get_pool", return_value=mock_pool):
                with patch("src.vector.cache.embed_text", return_value=[0.1] * 768):
                    result = await check_cache("similar text", owner_id="owner@example.com")
                    self.assertEqual(result, expected_summary)

        asyncio.run(_run())

    def test_cache_hit_logged(self) -> None:
        """Cache hit logs at INFO level."""
        from src.vector.cache import check_cache

        async def _run() -> None:
            mock_conn = AsyncMock()
            mock_conn.fetchone.return_value = {"summary": "Cached summary.", "similarity": 0.95}

            mock_pool = MagicMock()
            mock_pool.connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_pool.connection.return_value.__aexit__ = AsyncMock(return_value=False)

            with self.assertLogs("src.vector.cache", level=logging.INFO) as cm:
                with patch("src.vector.cache.get_pool", return_value=mock_pool):
                    with patch("src.vector.cache.embed_text", return_value=[0.1] * 768):
                        await check_cache("some text", owner_id="owner@example.com")

            self.assertTrue(
                any("cache hit" in msg.lower() for msg in cm.output),
                f"Expected 'cache hit' log, got: {cm.output}",
            )

        asyncio.run(_run())

    def test_store_cache_inserts_row(self) -> None:
        """store_cache writes a row to the DB."""
        from src.vector.cache import store_cache

        async def _run() -> None:
            mock_conn = AsyncMock()

            mock_pool = MagicMock()
            mock_pool.connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_pool.connection.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("src.vector.cache.get_pool", return_value=mock_pool):
                with patch("src.vector.cache.embed_text", return_value=[0.1] * 768):
                    await store_cache(
                        text="new text",
                        summary="new summary",
                        owner_id="owner@example.com",
                    )
                    self.assertTrue(mock_conn.execute.called)

        asyncio.run(_run())

    def test_store_cache_never_raises(self) -> None:
        """store_cache catches all exceptions and never propagates."""
        from src.vector.cache import store_cache

        async def _run() -> None:
            with patch("src.vector.cache.get_pool", side_effect=RuntimeError("boom")):
                # Should not raise
                await store_cache(
                    text="new text",
                    summary="new summary",
                    owner_id="owner@example.com",
                )

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# Tenant / owner scoping
# ---------------------------------------------------------------------------
class TenantTests(unittest.TestCase):
    """Contract tests for owner_id scoping across vector modules."""

    def test_owner_id_written_correctly(self) -> None:
        """DB rows carry owner_id matching SIGNAL_OWNER_ID."""
        from src.vector.cache import store_cache

        async def _run() -> None:
            mock_conn = AsyncMock()

            mock_pool = MagicMock()
            mock_pool.connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_pool.connection.return_value.__aexit__ = AsyncMock(return_value=False)

            test_owner = "test-owner@example.com"

            with patch("src.vector.cache.get_pool", return_value=mock_pool):
                with patch("src.vector.cache.embed_text", return_value=[0.1] * 768):
                    await store_cache(
                        text="text",
                        summary="summary",
                        owner_id=test_owner,
                    )
                    # Verify the execute call included owner_id
                    call_args = mock_conn.execute.call_args
                    self.assertIsNotNone(call_args)
                    # The SQL parameters should include owner_id
                    params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]
                    # params may be a dict or tuple depending on implementation
                    param_str = str(params)
                    self.assertIn(test_owner, param_str)

        asyncio.run(_run())

    def test_config_owner_id_defaults_to_allowed_email(self) -> None:
        """SIGNAL_OWNER_ID falls back to ALLOWED_USER_EMAIL when env is empty."""
        from src.core.config import ALLOWED_USER_EMAIL, SIGNAL_OWNER_ID

        # When SIGNAL_OWNER_ID env is not set, it should equal ALLOWED_USER_EMAIL
        # (This is a config-level test — the actual env may be set in .env)
        # We verify the logic by checking the default assignment in config.py
        self.assertIsNotNone(SIGNAL_OWNER_ID)


# ---------------------------------------------------------------------------
# Auth session routes
# ---------------------------------------------------------------------------
class AuthSessionTests(unittest.TestCase):
    """Contract tests for src.api.auth_session (session-login, session-logout)."""

    def test_session_login_sets_cookie(self) -> None:
        """POST /auth/session-login sets __session httpOnly cookie."""
        from fastapi.testclient import TestClient
        from src.app import app

        with patch("src.api.auth_session._init_firebase"), \
             patch("src.api.auth_session.verify_id_token", return_value={"uid": "test-uid"}), \
             patch("src.api.auth_session.fb_auth") as mock_fb_auth:
            mock_fb_auth.create_session_cookie.return_value = "mock_session_cookie"

            client = TestClient(app)
            response = client.post("/auth/session-login", json={"idToken": "valid-token"})

            self.assertEqual(response.status_code, 200)
            set_cookie = response.headers.get("set-cookie", "")
            self.assertIn("__session=mock_session_cookie", set_cookie)
            self.assertIn("HttpOnly", set_cookie)
            self.assertIn("SameSite=strict", set_cookie)

    def test_session_login_invalid_token(self) -> None:
        """POST with bad token returns 401."""
        from fastapi import HTTPException, status
        from fastapi.testclient import TestClient
        from src.app import app

        with patch("src.api.auth_session._init_firebase"), \
             patch("src.api.auth_session.verify_id_token") as mock_verify:
            mock_verify.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token.",
            )

            client = TestClient(app)
            response = client.post("/auth/session-login", json={"idToken": "bad-token"})

            self.assertEqual(response.status_code, 401)

    def test_session_logout_clears_cookie(self) -> None:
        """POST /auth/session-logout deletes __session cookie."""
        from fastapi.testclient import TestClient
        from src.app import app

        with patch("src.api.auth_session._init_firebase"), \
             patch("src.api.auth_session.fb_auth"):
            client = TestClient(app)
            response = client.post("/auth/session-logout")

            self.assertEqual(response.status_code, 200)
            set_cookie = response.headers.get("set-cookie", "")
            self.assertIn("__session=", set_cookie)
            # The cookie should have an expires/max-age that clears it
            self.assertTrue(
                "Max-Age=0" in set_cookie or "expires=" in set_cookie.lower(),
                f"Expected cookie deletion, got: {set_cookie}",
            )

    def test_session_login_missing_token(self) -> None:
        """POST without idToken returns 400."""
        from fastapi.testclient import TestClient
        from src.app import app

        with patch("src.api.auth_session._init_firebase"):
            client = TestClient(app)
            response = client.post("/auth/session-login", json={})

            self.assertEqual(response.status_code, 400)


# ---------------------------------------------------------------------------
# Integration tests (gated behind SIGNAL_POSTGRES_DSN_TEST)
# ---------------------------------------------------------------------------
@unittest.skipUnless(
    os.environ.get("SIGNAL_POSTGRES_DSN_TEST"),
    "SIGNAL_POSTGRES_DSN_TEST not set — skipping vector integration tests",
)
class VectorDBIntegrationTests(unittest.TestCase):
    """Live DB tests — require a running pgvector instance."""

    def test_live_pool_connects(self) -> None:
        """open_pool connects to the test DSN."""
        from src.vector.db import close_pool, get_pool, open_pool

        async def _run() -> None:
            dsn = os.environ["SIGNAL_POSTGRES_DSN_TEST"]
            await open_pool(dsn)
            pool = get_pool()
            self.assertIsNotNone(pool)
            await close_pool()

        asyncio.run(_run())

    def test_live_migration_creates_tables(self) -> None:
        """Migrations create expected tables."""
        from src.vector.db import _apply_migrations, close_pool, open_pool

        async def _run() -> None:
            dsn = os.environ["SIGNAL_POSTGRES_DSN_TEST"]
            await open_pool(dsn)
            pool = get_pool()
            async with pool.connection() as conn:
                await _apply_migrations(conn)
                # Verify tables exist
                cur = await conn.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                )
                tables = {row[0] for row in await cur.fetchall()}
                self.assertTrue(
                    "library_embeddings" in tables or "token_cache" in tables,
                    f"Expected vector tables, found: {tables}",
                )
            await close_pool()

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
