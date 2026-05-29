"""Async connection pool lifecycle and migrations for the Signal vector database."""

from __future__ import annotations

import logging
from pathlib import Path

from pgvector.psycopg import register_vector_async
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)

_pool: AsyncConnectionPool | None = None


async def open_pool(dsn: str) -> None:
    """Open the async connection pool, register pgvector, and apply migrations."""
    global _pool

    if not dsn:
        raise EnvironmentError(
            "SIGNAL_POSTGRES_DSN is not set. "
            "Vector DB pool cannot be initialised without a connection string."
        )

    _pool = AsyncConnectionPool(conninfo=dsn, open=False)
    await _pool.open()

    await _apply_migrations()

    async with _pool.connection() as conn:
        await register_vector_async(conn)

    logger.info("Vector DB pool ready")


async def close_pool() -> None:
    """Close the async connection pool if it was opened."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Vector DB pool closed")


def get_pool() -> AsyncConnectionPool:
    """Return the active pool. Raises RuntimeError if open_pool() was not called."""
    if _pool is None:
        raise RuntimeError("Vector DB pool not initialised. Call open_pool() first.")
    return _pool


async def _apply_migrations() -> None:
    """Execute the idempotent migration SQL via the pool."""
    if _pool is None:
        raise RuntimeError("Pool is not open. Cannot apply migrations.")

    migration_path = Path(__file__).parent / "migrations" / "001_init_vector.sql"
    sql = migration_path.read_text(encoding="utf-8")

    async with _pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
        await conn.commit()

    logger.info("Vector DB migrations applied")
