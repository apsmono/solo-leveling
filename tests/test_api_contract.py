"""API contract tests — verify dashboard-critical endpoints return expected shapes.

These tests act as a contract between solo-leveling (brain) and dashboard (frontend).
If an endpoint changes its response shape, these tests fail, signaling that the
dashboard may need updates before the SHA is bumped.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app import app


class ApiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}

    @patch("src.api.deps.verify_id_token")
    def test_dashboard_stats_contract(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/dashboard/stats", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("library", data)
        self.assertIn("integrations", data)
        self.assertIsInstance(data["library"], dict)
        self.assertIsInstance(data["integrations"], dict)

    @patch("src.api.deps.verify_id_token")
    def test_library_entries_contract(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/entries", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("entries", data)
        self.assertIn("total", data)
        self.assertIn("page", data)
        self.assertIn("per_page", data)
        self.assertIsInstance(data["entries"], list)
        self.assertIsInstance(data["total"], int)

    @patch("src.api.deps.verify_id_token")
    def test_library_sections_contract(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/sections", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("sections", data)
        self.assertIsInstance(data["sections"], list)

    @patch("src.api.deps.verify_id_token")
    def test_library_graph_contract(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/graph", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertIsInstance(data["nodes"], list)
        self.assertIsInstance(data["edges"], list)

    @patch("src.api.deps.verify_id_token")
    def test_library_timeline_contract(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/timeline", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("days", data)
        self.assertIn("total", data)
        self.assertIn("daily_counts", data)
        self.assertIsInstance(data["days"], list)

    @patch("src.api.deps.verify_id_token")
    def test_analysis_tags_contract(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/analysis/tags", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("frequencies", data)
        self.assertIn("trending", data)
        self.assertIn("orphan_tags", data)
        self.assertIn("co_occurrence", data)

    @patch("src.api.deps.verify_id_token")
    def test_planning_goals_contract(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/planning/goals", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("goals", data)
        self.assertIn("active", data)
        self.assertIn("completed", data)
        self.assertIn("paused", data)

    def test_command_contract_no_auth(self) -> None:
        res = self.client.post("/command", json={"text": "health"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("status", data)
        self.assertIn("reply", data)

    @patch("src.api.deps.verify_id_token")
    @patch("src.autopilot.loop.plan_steps", return_value=[])
    def test_autopilot_tasks_contract(self, _mock_plan: MagicMock, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/autopilot/tasks", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("tasks", data)
        self.assertIsInstance(data["tasks"], list)

    @patch("src.api.deps.verify_id_token")
    def test_autopilot_approvals_contract(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/autopilot/approvals", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("approvals", data)
        self.assertIsInstance(data["approvals"], list)


if __name__ == "__main__":
    unittest.main()
