"""Public facade for the Signal vector database module."""

from __future__ import annotations

from src.vector.db import close_pool, get_pool, open_pool

__all__ = ["close_pool", "get_pool", "open_pool"]
