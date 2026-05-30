"""
Test stubs for Phase 3: Knowledge Library — AI Guide API (Wave 0).

These tests define the contract for src.api.guide:
- POST /api/v1/guide/command  {text: "..."}
- GET  /api/v1/guide/status
- POST /api/v1/guide/park     {text: "..."}

All tests run offline (mocked auth + dependencies).
"""

from __future__ import annotations

import os
import unittest
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv

load_dotenv()

# Conditional import — module does not exist yet in Wave 0
_guide_api_available = False

try:
    from src.api import guide as _guide_mod

    _guide_api_available = True
except ImportError:
    pass


@unittest.skipUnless(_guide_api_available, "src.api.guide not yet implemented — skipping")
class GuideAPITests(unittest.TestCase):
    """Contract tests for src.api.guide endpoints."""

    def setUp(self) -> None:
        from fastapi.testclient import TestClient
        from src.app import app

        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}

    def test_guide_command_parses_intent(self) -> None:
        """POST /api/v1/guide/command parses intent and returns structured response."""
        mock_intent_result = {
            "intent": "library_search",
            "params": {"query": "search library"},
            "confidence": 0.95,
        }

        with patch("src.api.guide.require_auth", return_value=self.mock_user):
            with patch("src.api.guide.parse_intent", return_value=mock_intent_result):
                response = self.client.post(
                    "/api/v1/guide/command",
                    json={"text": "search library"},
                    headers={"Authorization": "Bearer valid-token"},
                )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("intent", data)
        self.assertEqual(data["intent"], "library_search")

    def test_guide_command_missing_text_returns_400(self) -> None:
        """POST /api/v1/guide/command with empty body returns 400."""
        with patch("src.api.guide.require_auth", return_value=self.mock_user):
            response = self.client.post(
                "/api/v1/guide/command",
                json={},
                headers={"Authorization": "Bearer valid-token"},
            )

        self.assertEqual(response.status_code, 400)

    def test_guide_status_returns_metrics(self) -> None:
        """GET /api/v1/guide/status returns guide metrics."""
        with patch("src.api.guide.require_auth", return_value=self.mock_user):
            response = self.client.get(
                "/api/v1/guide/status",
                headers={"Authorization": "Bearer valid-token"},
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("metrics", data)

    def test_guide_park_creates_entry(self) -> None:
        """POST /api/v1/guide/park creates a library entry and returns entry_id."""
        mock_store = MagicMock()
        mock_store.add_entry.return_value = "parked-entry-123"

        with patch("src.api.guide.require_auth", return_value=self.mock_user):
            with patch("src.api.guide._get_store", return_value=mock_store):
                response = self.client.post(
                    "/api/v1/guide/park",
                    json={"text": "stray thought"},
                    headers={"Authorization": "Bearer valid-token"},
                )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("entry_id", data)
        self.assertEqual(data["entry_id"], "parked-entry-123")

    def test_guide_park_missing_text_returns_400(self) -> None:
        """POST /api/v1/guide/park with empty body returns 400."""
        with patch("src.api.guide.require_auth", return_value=self.mock_user):
            response = self.client.post(
                "/api/v1/guide/park",
                json={},
                headers={"Authorization": "Bearer valid-token"},
            )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
