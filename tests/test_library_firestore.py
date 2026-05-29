from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.core.library_store import _FileLibraryStore, _FirestoreLibraryStore


class FirestoreLibraryStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_root = Path(self.temp_dir.name)
        self.library_root = self.temp_root / "library"
        self.index_path = self.library_root / "index.json"
        self.library_root.mkdir(parents=True, exist_ok=True)

    def test_firestore_store_delegates_reads_to_file_store_on_firestore_failure(self) -> None:
        """If Firestore read fails, file store fallback is used."""
        store = _FirestoreLibraryStore(
            project_root=self.temp_root,
            library_root=self.library_root,
            index_path=self.index_path,
        )
        # Write a file directly to the filesystem
        file_store = _FileLibraryStore(self.temp_root, self.library_root, self.index_path)
        file_store.save_entry("term", "Test Term", "A test definition", status="active")

        # Firestore will fail (no mock client), but file store fallback should work
        result = store.search_entries("Test", limit=5)
        self.assertTrue(len(result) > 0)
        self.assertIn("Test Term", str(result))

    def test_firestore_store_counts_entries(self) -> None:
        store = _FirestoreLibraryStore(
            project_root=self.temp_root,
            library_root=self.library_root,
            index_path=self.index_path,
        )
        file_store = _FileLibraryStore(self.temp_root, self.library_root, self.index_path)
        file_store.save_entry("term", "T1", "D1", status="active")
        file_store.save_entry("term", "T2", "D2", status="active")

        # Should count from filesystem since Firestore has no mock
        count = store.count_entries("term")
        self.assertEqual(count, 2)

    def test_firestore_store_dual_write_creates_local_file(self) -> None:
        store = _FirestoreLibraryStore(
            project_root=self.temp_root,
            library_root=self.library_root,
            index_path=self.index_path,
        )
        path = store.save_entry("term", "Dual Write", "Test", status="active")
        # File should exist even if Firestore mock is not set up
        self.assertTrue((self.temp_root / path).exists())

    def test_file_store_list_sections(self) -> None:
        store = _FileLibraryStore(self.temp_root, self.library_root, self.index_path)
        sections = store.list_sections()
        self.assertIn("term", sections)
        self.assertIn("book", sections)
        self.assertIn("article", sections)

    def test_file_store_list_tags(self) -> None:
        store = _FileLibraryStore(self.temp_root, self.library_root, self.index_path)
        store.save_entry("term", "T1", "D1", status="active", tags=["ai", "ml"])
        store.save_entry("term", "T2", "D2", status="active", tags=["ml", "python"])
        tags = store.list_tags()
        self.assertIn("ai", tags)
        self.assertIn("ml", tags)
        self.assertIn("python", tags)


if __name__ == "__main__":
    unittest.main()
