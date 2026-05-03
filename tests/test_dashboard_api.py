"""Unit tests for dashboard API endpoints."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app import app


class DashboardApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}

    @patch("src.api.deps.verify_id_token")
    def test_dashboard_stats(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        with patch("src.core.libraries._count_entries", return_value=3):
            response = self.client.get(
                "/api/v1/dashboard/stats",
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("library", data)
        self.assertIn("integrations", data)

    @patch("src.api.deps.verify_id_token")
    def test_dashboard_health(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        response = self.client.get(
            "/api/v1/dashboard/health",
            headers={"Authorization": "Bearer valid-token"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("integrations", data)

    @patch("src.api.deps.verify_id_token")
    def test_list_commands(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        with patch("src.api.commands.USE_FIRESTORE_REMINDERS", True):
            with patch("src.integrations.firebase.firestore.list_recent_commands", return_value=[{"text": "hello"}]):
                response = self.client.get(
                    "/api/v1/commands",
                    headers={"Authorization": "Bearer valid-token"},
                )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    @patch("src.api.deps.verify_id_token")
    def test_list_commands_without_firestore(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        with patch("src.api.commands.USE_FIRESTORE_REMINDERS", False):
            response = self.client.get(
                "/api/v1/commands",
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    @patch("src.api.deps.verify_id_token")
    def test_list_reminders(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        with patch("src.api.reminders.format_pending_reminders", return_value="No pending reminders."):
            response = self.client.get(
                "/api/v1/reminders",
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("pending", response.json())

    @patch("src.api.deps.verify_id_token")
    def test_add_reminder(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        with patch("src.api.reminders.create_reminder", return_value={"id": "r1", "message": "test"}):
            response = self.client.post(
                "/api/v1/reminders",
                json={"message": "test", "run_at": "2026-05-03T10:00"},
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")

    @patch("src.api.deps.verify_id_token")
    def test_add_reminder_missing_fields(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        response = self.client.post(
            "/api/v1/reminders",
            json={"message": ""},
            headers={"Authorization": "Bearer valid-token"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "error")

    @patch("src.api.deps.verify_id_token")
    def test_delete_reminder(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        with patch("src.api.reminders.USE_FIRESTORE_REMINDERS", True):
            with patch("src.integrations.firebase.firestore._client") as mock_client:
                response = self.client.delete(
                    "/api/v1/reminders/r1",
                    headers={"Authorization": "Bearer valid-token"},
                )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_dashboard_stats_unauthorized(self) -> None:
        response = self.client.get("/api/v1/dashboard/stats")
        self.assertEqual(response.status_code, 401)

    def test_healthz_no_auth(self) -> None:
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_command_no_auth(self) -> None:
        response = self.client.post("/command", json={"text": "status"})
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
