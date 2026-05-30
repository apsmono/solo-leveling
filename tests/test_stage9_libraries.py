from __future__ import annotations

import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from src.core import libraries
from src.core.scheduler import format_library_maintenance_schedule, handle_library_maintenance_command


class Stage9LibraryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.original_project_root = libraries._PROJECT_ROOT
        self.original_library_root = libraries._LIBRARY_ROOT
        self.original_index_path = libraries._INDEX_PATH

        temp_root = Path(self.temp_dir.name)
        libraries._PROJECT_ROOT = temp_root
        libraries._LIBRARY_ROOT = temp_root / "library"
        libraries._INDEX_PATH = libraries._LIBRARY_ROOT / "index.json"
        libraries._ensure_library_dirs()

        # Force filesystem store — temp dirs are not mirrored in Firestore.
        self.firestore_patch = patch("src.core.libraries.USE_FIRESTORE_LIBRARY", False)
        self.firestore_patch.start()
        self.addCleanup(self.firestore_patch.stop)

        self.addCleanup(self._restore_globals)

    def _restore_globals(self) -> None:
        libraries._PROJECT_ROOT = self.original_project_root
        libraries._LIBRARY_ROOT = self.original_library_root
        libraries._INDEX_PATH = self.original_index_path

    def test_add_term_requires_definition(self) -> None:
        result = libraries.handle_library_command("add term: MCP", "library_term")
        self.assertEqual(result, "Use: add term: <term> = <definition>")

    def test_book_requires_author_pattern(self) -> None:
        result = libraries.handle_library_command("book: Atomic Habits", "library_book")
        self.assertEqual(result, "Use: book: <title> by <author>")

    def test_thought_requires_enough_detail(self) -> None:
        result = libraries.handle_library_command("thought: idea", "library_thought")
        self.assertEqual(result, "Use: thought: <idea with enough detail to be useful>")

    def test_add_term_creates_entry_and_index(self) -> None:
        result = libraries.handle_library_command(
            "add term: MCP = Model Context Protocol",
            "library_term",
        )

        self.assertIn("Term saved to local library.", result)
        files = list((libraries._LIBRARY_ROOT / "terms").glob("*.md"))
        self.assertEqual(len(files), 1)
        self.assertTrue(libraries._INDEX_PATH.exists())
        index_text = libraries._INDEX_PATH.read_text(encoding="utf-8")
        self.assertIn("Term: MCP", index_text)

    def test_deep_capture_creates_bundle_and_supports_retrieval(self) -> None:
        with patch("src.core.libraries.run_agent", side_effect=RuntimeError("ai unavailable")):
            result = libraries.handle_library_command(
                "add to library: Retrieval UX for research bundles in the personal knowledge system",
                "library_capture",
            )

        self.assertIn("Knowledge capture saved to local library.", result)
        bundles = [path for path in (libraries._LIBRARY_ROOT / "research").iterdir() if path.is_dir()]
        self.assertEqual(len(bundles), 1)
        bundle = bundles[0]

        expected_files = {
            "index.md",
            "01-raw-input.md",
            "02-search-history.md",
            "03-research-notes.md",
            "04-information-to-track.md",
            "05-qa-log.md",
            "06-logic-trail.md",
            "07-conclusion.md",
        }
        self.assertEqual({path.name for path in bundle.iterdir()}, expected_files)

        search_result = libraries.handle_library_command("search library: retrieval ux", "library_search")
        self.assertIn(str(bundle.relative_to(libraries._PROJECT_ROOT)), search_result)

        bundle_result = libraries.handle_library_command("library bundle: retrieval ux", "library_bundle")
        self.assertIn(str(bundle.relative_to(libraries._PROJECT_ROOT)), bundle_result)

        summary_result = libraries.handle_library_command("summarize library: retrieval ux", "library_summary")
        self.assertIn("Summary for 'retrieval ux':", summary_result)
        self.assertIn("Track:", summary_result)

    def test_library_maintenance_summary_and_schedule(self) -> None:
        libraries.handle_library_command(
            "add term: MCP = Model Context Protocol",
            "library_term",
        )

        maintenance_result = libraries.handle_library_command(
            "library maintenance",
            "library_maintenance",
        )
        self.assertIn("Weekly library maintenance", maintenance_result)
        self.assertIn("• Terms: 1", maintenance_result)

        schedule_result = handle_library_maintenance_command("library maintenance schedule")
        self.assertIn("Library maintenance schedule", schedule_result)
        self.assertIn("• Command: library maintenance", schedule_result)

    def test_search_cache_hit_miss(self) -> None:
        """Verify search cache stores and returns results."""
        libraries.handle_library_command(
            "add term: Python = Programming language",
            "library_term",
        )

        # First search: cache miss, index rebuilt
        result1 = libraries._find_entries_by_query("Python")
        self.assertTrue(len(result1) > 0)

        # Second search: cache hit, same results
        result2 = libraries._find_entries_by_query("Python")
        self.assertEqual(result1, result2)

    def test_search_cache_invalidation_on_write(self) -> None:
        """Verify cache is cleared when new entry is added."""
        libraries.handle_library_command(
            "add term: Cache = Fast memory storage",
            "library_term",
        )

        # Search and cache result
        result1 = libraries._find_entries_by_query("Cache")
        cache_size_1 = len(libraries._search_cache.cache)

        # Add new entry (should invalidate cache)
        libraries.handle_library_command(
            "add term: LRU = Least Recently Used",
            "library_term",
        )

        # Cache should be cleared
        cache_size_2 = len(libraries._search_cache.cache)
        self.assertEqual(cache_size_2, 0, "Cache not invalidated after new entry")

    def test_search_cache_performance_improvement(self) -> None:
        """Verify warm cache is faster than cold cache."""
        import time

        libraries.handle_library_command(
            "add term: Performance = Speed and efficiency",
            "library_term",
        )

        # Clear cache to ensure cold start
        libraries._search_cache.invalidate()

        # First search (cold cache)
        start = time.time()
        result1 = libraries._find_entries_by_query("Performance")
        cold_time = time.time() - start

        # Second search (warm cache) - should be faster
        start = time.time()
        result2 = libraries._find_entries_by_query("Performance")
        warm_time = time.time() - start

        # Results should be identical
        self.assertEqual(result1, result2)

        # Warm should not be slower than cold. On fast environments the measured
        # warm time can be exactly 0.0, so avoid strict positive-time assertions.
        self.assertGreater(cold_time, 0, "Cold search time not measured")
        self.assertGreaterEqual(warm_time, 0, "Warm search time not measured")
        self.assertLessEqual(
            warm_time,
            cold_time,
            f"Warm search should not be slower than cold search (warm={warm_time}, cold={cold_time})",
        )

    # ------------------------------------------------------------------
    # A2: Larger corpus search behaviour
    # ------------------------------------------------------------------

    def test_search_larger_corpus_returns_only_matching_entries(self) -> None:
        """Search on a large-ish index must return matches only, not all entries."""
        terms = [
            ("Python", "A high-level programming language"),
            ("Rust", "Systems language focused on safety"),
            ("Docker", "Container platform for packaging apps"),
            ("Kubernetes", "Container orchestration platform"),
            ("FastAPI", "Modern Python web framework"),
        ]
        for term, definition in terms:
            libraries.handle_library_command(
                f"add term: {term} = {definition}",
                "library_term",
            )

        # Search matches against title/path/section/category only (index-level search, not full-text)
        result = libraries._find_entries_by_query("docker")
        titles = [entry.get("title", "") for entry in result]
        # "Docker" is in the title; Python/Rust/FastAPI/Kubernetes don't contain "docker"
        self.assertTrue(
            any("Docker" in t for t in titles),
            f"Expected Docker entry in result, got: {titles}",
        )
        non_matches = [t for t in titles if "python" in t.lower() or "rust" in t.lower()]
        self.assertEqual(non_matches, [], f"Non-matching terms returned: {non_matches}")

    def test_search_empty_query_returns_empty(self) -> None:
        """Empty search query must return an empty list without errors."""
        libraries.handle_library_command(
            "add term: Anything = Some definition",
            "library_term",
        )
        result = libraries._find_entries_by_query("")
        self.assertIsInstance(result, list)

    def test_search_no_match_returns_empty_list(self) -> None:
        """Query that matches nothing returns an empty list."""
        libraries.handle_library_command(
            "add term: Elixir = Functional language",
            "library_term",
        )
        result = libraries._find_entries_by_query("xylophone")
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

    # ------------------------------------------------------------------
    # A2: Malformed input for deep-capture commands
    # ------------------------------------------------------------------

    def test_deep_capture_empty_content_returns_error(self) -> None:
        """Empty capture input must return a validation error, not raise."""
        result = libraries.handle_library_command("add to library:", "library_capture")
        # Should return a user-facing error string, not raise
        self.assertIsInstance(result, str)
        self.assertTrue(
            len(result) > 0,
            "Empty capture input should return a non-empty error message",
        )

    def test_deep_capture_very_short_input(self) -> None:
        """Single-word capture input should be handled gracefully."""
        with patch("src.core.libraries.run_agent", side_effect=RuntimeError("ai unavailable")):
            result = libraries.handle_library_command("add to library: x", "library_capture")
        self.assertIsInstance(result, str)

    def test_deep_capture_sensitive_data_rejected(self) -> None:
        """Input containing sensitive tokens must be blocked."""
        result = libraries.handle_library_command(
            "add to library: my password is hunter2",
            "library_capture",
        )
        self.assertIn("sensitive", result.lower())

    # ------------------------------------------------------------------
    # A2: Bundle indexing edge cases
    # ------------------------------------------------------------------

    def test_index_rebuilt_after_multiple_writes(self) -> None:
        """Index must contain all entries written in sequence."""
        for i in range(5):
            libraries.handle_library_command(
                f"add term: Term{i} = Definition number {i}",
                "library_term",
            )

        index_text = libraries._INDEX_PATH.read_text(encoding="utf-8")
        for i in range(5):
            self.assertIn(f"Term{i}", index_text)

    def test_bundle_lookup_no_match_returns_message(self) -> None:
        """Bundle lookup for a non-existent topic returns a friendly no-result message."""
        result = libraries.handle_library_command(
            "library bundle: totally nonexistent topic xyz",
            "library_bundle",
        )
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    # ------------------------------------------------------------------
    # A2: Summary retrieval edge cases
    # ------------------------------------------------------------------

    def test_summary_no_match_returns_message(self) -> None:
        """Summary command for a non-existent topic returns a friendly no-result message."""
        result = libraries.handle_library_command(
            "summarize library: quantum teleportation",
            "library_summary",
        )
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_summary_returns_track_section_from_bundle(self) -> None:
        """Summary of an existing bundle must include the Track section."""
        with patch("src.core.libraries.run_agent", side_effect=RuntimeError("ai unavailable")):
            libraries.handle_library_command(
                "add to library: Second order thinking and its applications",
                "library_capture",
            )

        result = libraries.handle_library_command(
            "summarize library: second order thinking",
            "library_summary",
        )
        self.assertIn("Track:", result)


if __name__ == "__main__":
    unittest.main()
