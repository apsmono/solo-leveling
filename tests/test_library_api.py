"""Tests for /api/v1/library REST endpoints."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app import app


class LibraryApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}

    @patch("src.api.deps.verify_id_token")
    def test_list_sections(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/sections", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("sections", data)
        self.assertIsInstance(data["sections"], list)
        self.assertIn("term", data["sections"])

    @patch("src.api.deps.verify_id_token")
    def test_list_entries_paginated(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/entries?page=1&per_page=5", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("entries", data)
        self.assertIn("total", data)
        self.assertIn("page", data)
        self.assertIn("per_page", data)
        self.assertIsInstance(data["entries"], list)

    @patch("src.api.deps.verify_id_token")
    def test_list_entries_filter_by_section(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/entries?section=terms", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        for e in data["entries"]:
            self.assertIn("term", str(e.get("section", "")).lower())

    @patch("src.api.deps.verify_id_token")
    def test_list_entries_filter_by_search(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/entries?search=MCP", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data["entries"], list)

    @patch("src.api.deps.verify_id_token")
    def test_get_entry_found(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        list_res = self.client.get("/api/v1/library/entries?per_page=1", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(list_res.status_code, 200)
        entries = list_res.json()["entries"]
        if not entries:
            self.skipTest("No library entries to test with.")
        entry_id = entries[0]["id"]

        res = self.client.get(f"/api/v1/library/entries/{entry_id}", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["id"], entry_id)
        self.assertIn("title", data)
        self.assertIn("markdown", data)
        self.assertIn("related", data)

    @patch("src.api.deps.verify_id_token")
    def test_get_entry_not_found(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/entries/nonexistent-id-12345", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 404)

    @patch("src.api.deps.verify_id_token")
    def test_list_tags(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/tags", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("tags", data)
        self.assertIsInstance(data["tags"], list)

    def test_list_sections_unauthorized(self) -> None:
        res = self.client.get("/api/v1/library/sections")
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
