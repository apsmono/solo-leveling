"""
Tests for Phase 3: Knowledge Library — AI Guide API.

These tests verify src.api.guide endpoints:
- POST /api/v1/guide/command  {text: "..."}
- GET  /api/v1/guide/status
- POST /api/v1/guide/park     {text: "..."}

All tests run offline (mocked auth + dependencies).
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv

load_dotenv()

# Mock firebase_admin before importing app (module may not be installed in CI)
_mock_firebase_admin = MagicMock()
_mock_firebase_admin.credentials.Certificate.from_json = MagicMock(return_value=MagicMock())
_mock_firebase_admin.initialize_app = MagicMock(return_value=MagicMock())
sys.modules["firebase_admin"] = _mock_firebase_admin
sys.modules["firebase_admin.credentials"] = _mock_firebase_admin.credentials
sys.modules["firebase_admin.auth"] = _mock_firebase_admin.auth

# Set ALLOWED_USER_EMAIL so auth checks pass
os.environ["ALLOWED_USER_EMAIL"] = "owner@example.com"

from fastapi.testclient import TestClient
from src.app import app


class GuideAPITests(unittest.TestCase):
    """Contract tests for src.api.guide endpoints."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}
        _mock_firebase_admin.auth.verify_id_token.reset_mock(side_effect=True)
        _mock_firebase_admin.auth.verify_id_token.return_value = self.mock_user

    def test_guide_command_parses_intent(self) -> None:
        """POST /api/v1/guide/command parses intent and returns reply."""
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

    def test_guide_command_missing_text_returns_400(self) -> None:
        """POST /api/v1/guide/command with empty body returns 400."""
        response = self.client.post(
            "/api/v1/guide/command",
            json={},
            headers={"Authorization": "Bearer valid-token"},
        )

        self.assertEqual(response.status_code, 400)

    def test_guide_status_returns_metrics(self) -> None:
        """GET /api/v1/guide/status returns guide metrics."""
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

    def test_guide_park_saves_thought(self) -> None:
        """POST /api/v1/guide/park saves a thought and returns success."""
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

    def test_guide_park_missing_text_returns_400(self) -> None:
        """POST /api/v1/guide/park with empty body returns 400."""
        response = self.client.post(
            "/api/v1/guide/park",
            json={},
            headers={"Authorization": "Bearer valid-token"},
        )

        self.assertEqual(response.status_code, 400)

    def test_guide_park_handler_called_correctly(self) -> None:
        """Park endpoint constructs the correct command text for the handler."""
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
