"""Gzip compression and chunking for Firestore document size limits.

Firestore has a 1,048,576 byte document size limit. This module provides
transparent compression and automatic chunking for large markdown content.

Usage:
    stored, is_compressed, needs_chunking = compress_content(markdown)
    # Store in Firestore
    if needs_chunking:
        chunks = chunk_content(markdown)
        # Store chunks in subcollection
    else:
        # Store stored directly in document

    # Later:
    if needs_chunking:
        markdown = reassemble_chunks(chunks)
    elif is_compressed:
        markdown = decompress_content(stored, is_compressed=True)
    else:
        markdown = stored
"""

from __future__ import annotations

import base64
import gzip
import logging

logger = logging.getLogger(__name__)

# Firestore doc limit is 1,048,576 bytes. Leave ~10% headroom for other fields.
_MAX_DOC_BYTES = 950_000
_CHUNK_SIZE = 900_000  # bytes, well under 1MB for base64 chunks


def compress_content(markdown: str) -> tuple[str, bool, bool]:
    """Compress markdown content for Firestore storage.

    Returns:
        (stored_content, is_compressed, needs_chunking)
        - stored_content: the string to store (plain, gzip+base64, or None if chunked)
        - is_compressed: True if content is gzip+base64 encoded
        - needs_chunking: True if content must be split into subcollection chunks
    """
    raw_bytes = markdown.encode("utf-8")

    # If raw fits, store as-is
    if len(raw_bytes) < _MAX_DOC_BYTES:
        return markdown, False, False

    # Try gzip compression
    compressed = gzip.compress(raw_bytes, compresslevel=9)
    b64 = base64.b64encode(compressed).decode("ascii")
    b64_bytes = b64.encode("utf-8")

    if len(b64_bytes) < _MAX_DOC_BYTES:
        return b64, True, False

    # Still too large: needs chunking
    return b64, True, True


def decompress_content(stored: str, is_compressed: bool) -> str:
    """Reverse compression."""
    if not is_compressed:
        return stored
    compressed = base64.b64decode(stored)
    return gzip.decompress(compressed).decode("utf-8")


def chunk_content(markdown: str, chunk_size: int = _CHUNK_SIZE) -> list[str]:
    """Split compressed content into chunks that fit Firestore docs.

    Each chunk is gzip+base64 encoded independently for self-containment.
    This is simpler but less efficient than splitting the pre-compressed
    base64 string. For library entries, the simplicity trade-off is worth it.

    Args:
        markdown: The full markdown content.
        chunk_size: Maximum size in bytes for each chunk's base64 string.

    Returns:
        List of chunk strings (gzip+base64 encoded).
    """
    raw_bytes = markdown.encode("utf-8")
    compressed = gzip.compress(raw_bytes, compresslevel=9)
    b64 = base64.b64encode(compressed).decode("ascii")
    b64_bytes = b64.encode("utf-8")

    chunks: list[str] = []
    for i in range(0, len(b64_bytes), chunk_size):
        chunk = b64_bytes[i : i + chunk_size].decode("ascii")
        chunks.append(chunk)

    logger.info(
        "Chunked %d bytes of markdown into %d chunks",
        len(raw_bytes),
        len(chunks),
    )
    return chunks


def reassemble_chunks(chunks: list[str]) -> str:
    """Reassemble chunked content back to original markdown."""
    b64 = "".join(chunks)
    compressed = base64.b64decode(b64)
    return gzip.decompress(compressed).decode("utf-8")
