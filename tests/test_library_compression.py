from __future__ import annotations

import unittest

from src.core.library_compression import (
    compress_content,
    decompress_content,
    chunk_content,
    reassemble_chunks,
)


class LibraryCompressionTests(unittest.TestCase):
    def test_small_content_uncompressed(self) -> None:
        text = "Small markdown content"
        stored, compressed, chunked = compress_content(text)
        self.assertEqual(stored, text)
        self.assertFalse(compressed)
        self.assertFalse(chunked)

    def test_large_content_compressed(self) -> None:
        text = "x" * 2_000_000  # 2MB of text
        stored, compressed, chunked = compress_content(text)
        self.assertTrue(compressed)
        self.assertFalse(chunked)
        self.assertLess(len(stored), len(text))

    def test_very_large_content_chunked(self) -> None:
        # Use random-like content that doesn't compress well
        import random
        random.seed(42)
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
        text = "".join(random.choice(chars) for _ in range(10_000_000))
        stored, compressed, chunked = compress_content(text)
        self.assertTrue(chunked)

    def test_roundtrip_compression(self) -> None:
        text = "Hello world" * 1000
        stored, compressed, _ = compress_content(text)
        result = decompress_content(stored, compressed)
        self.assertEqual(result, text)

    def test_roundtrip_chunking(self) -> None:
        text = "Chunked content" * 100_000
        chunks = chunk_content(text, chunk_size=1000)
        self.assertGreater(len(chunks), 1)
        result = reassemble_chunks(chunks)
        self.assertEqual(result, text)

    def test_uncompressed_roundtrip(self) -> None:
        text = "No compression needed"
        stored, compressed, _ = compress_content(text)
        result = decompress_content(stored, compressed)
        self.assertEqual(result, text)

    def test_empty_string(self) -> None:
        text = ""
        stored, compressed, chunked = compress_content(text)
        self.assertEqual(stored, text)
        self.assertFalse(compressed)
        self.assertFalse(chunked)

    def test_unicode_content(self) -> None:
        text = "日本語コンテンツ 🎌 " * 5000
        stored, compressed, chunked = compress_content(text)
        result = decompress_content(stored, compressed)
        self.assertEqual(result, text)


if __name__ == "__main__":
    unittest.main()
