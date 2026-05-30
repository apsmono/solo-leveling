"""
Tests for Phase 3: Knowledge Library — AI Guide API.

These tests verify src.api.guide endpoints:
- POST /api/v1/guide/command  {text: "..."}
- GET  /api/v1/guide/status
- POST /api/v1/guide/park     {text: "..."}

All tests run offline (mocked auth + dependencies).
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app import app


class GuideAPITests(unittest.TestCase):
    """Contract tests for src.api.guide endpoints."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}

    @patch("src.api.deps.verify_id_token")
    def test_guide_command_parses_intent(self, mock_verify: MagicMock) -> None:
        """POST /api/v1/guide/command parses intent and returns reply."""
        mock_verify.return_value = self.mock_user
        with patch("src.api.guide.route_command", return_value="Here are your results."):
            response = self.client.post(
                "/api/v1/guide/command",
                json={"text": "search library"},
                headers={"Authorization": "Bearer valid-token"},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["reply"], "Here are your results.")

    @patch("src.api.deps.verify_id_token")
    def test_guide_command_missing_text_returns_400(self, mock_verify: MagicMock) -> None:
        """POST /api/v1/guide/command with empty body returns 400."""
        mock_verify.return_value = self.mock_user
        response = self.client.post(
            "/api/v1/guide/command",
            json={},
            headers={"Authorization": "Bearer valid-token"},
        )

        self.assertEqual(response.status_code, 400)

    @patch("src.api.deps.verify_id_token")
    def test_guide_status_returns_metrics(self, mock_verify: MagicMock) -> None:
        """GET /api/v1/guide/status returns guide metrics."""
        mock_verify.return_value = self.mock_user
        mock_index = {
            "entries": [
                {"updated_at": "2026-05-30T01:00:00+00:00"},
                {"captured_at": "2026-05-29T10:00:00+00:00"},
            ]
        }
        mock_store = MagicMock()
        mock_store.build_index.return_value = mock_index

        with patch("src.api.guide._get_store", return_value=mock_store):
            response = self.client.get(
                "/api/v1/guide/status",
                headers={"Authorization": "Bearer valid-token"},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("metrics", data)
        metrics = data["metrics"]
        self.assertIn("entries", metrics)
        self.assertIn("recent_captures", metrics)
        self.assertEqual(metrics["entries"], 2)

    @patch("src.api.deps.verify_id_token")
    def test_guide_park_saves_thought(self, mock_verify: MagicMock) -> None:
        """POST /api/v1/guide/park saves a thought and returns success."""
        mock_verify.return_value = self.mock_user
        with patch("src.api.guide.handle_library_command", return_value="Thought saved."):
            response = self.client.post(
                "/api/v1/guide/park",
                json={"text": "stray thought"},
                headers={"Authorization": "Bearer valid-token"},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["message"], "Thought parked.")

    @patch("src.api.deps.verify_id_token")
    def test_guide_park_missing_text_returns_400(self, mock_verify: MagicMock) -> None:
        """POST /api/v1/guide/park with empty body returns 400."""
        mock_verify.return_value = self.mock_user
        response = self.client.post(
            "/api/v1/guide/park",
            json={},
            headers={"Authorization": "Bearer valid-token"},
        )

        self.assertEqual(response.status_code, 400)

    @patch("src.api.deps.verify_id_token")
    def test_guide_park_handler_called_correctly(self, mock_verify: MagicMock) -> None:
        """Park endpoint constructs the correct command text for the handler."""
        mock_verify.return_value = self.mock_user
        mock_handler = MagicMock(return_value="Thought saved.")

        with patch("src.api.guide.handle_library_command", mock_handler):
            response = self.client.post(
                "/api/v1/guide/park",
                json={"text": "remember to call mom"},
                headers={"Authorization": "Bearer valid-token"},
            )

        self.assertEqual(response.status_code, 200)
        mock_handler.assert_called_once_with(
            text="thought: remember to call mom",
            intent="library_thought",
        )


if __name__ == "__main__":
    unittest.main()
