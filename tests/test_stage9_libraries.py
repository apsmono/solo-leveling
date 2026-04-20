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


if __name__ == "__main__":
    unittest.main()