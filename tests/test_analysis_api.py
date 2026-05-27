"""Tests for analysis, graph, timeline, and planning REST endpoints."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app import app


class AnalysisApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}

    @patch("src.api.deps.verify_id_token")
    def test_graph(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/graph", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertIsInstance(data["nodes"], list)
        self.assertIsInstance(data["edges"], list)

    @patch("src.api.deps.verify_id_token")
    def test_timeline(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/timeline", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("days", data)
        self.assertIn("total", data)

    @patch("src.api.deps.verify_id_token")
    def test_timeline_filter_section(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/library/timeline?section=terms", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data["days"], list)

    @patch("src.api.deps.verify_id_token")
    def test_analysis_tags(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/analysis/tags", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("frequencies", data)
        self.assertIn("trending", data)
        self.assertIn("orphan_tags", data)
        self.assertIn("co_occurrence", data)

    @patch("src.api.deps.verify_id_token")
    def test_analysis_gaps(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/analysis/gaps", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("empty_sections", data)
        self.assertIn("stale_entries", data)
        self.assertIn("orphan_entries", data)
        self.assertIn("section_counts", data)

    @patch("src.api.deps.verify_id_token")
    def test_analysis_activity(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/analysis/activity", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("daily_counts", data)
        self.assertIn("section_growth", data)
        self.assertIn("capture_velocity", data)

    @patch("src.api.deps.verify_id_token")
    def test_planning_goals(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/planning/goals", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("goals", data)
        self.assertIn("active", data)
        self.assertIn("completed", data)

    @patch("src.api.deps.verify_id_token")
    def test_planning_projects(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/planning/projects", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("projects", data)

    @patch("src.api.deps.verify_id_token")
    def test_planning_reviews(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/planning/reviews", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("reviews", data)

    @patch("src.api.deps.verify_id_token")
    def test_planning_focus(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/planning/focus", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("suggestions", data)
        self.assertIn("active_goals_count", data)

    @patch("src.api.deps.verify_id_token")
    def test_graph_unauthorized(self, mock_verify: MagicMock) -> None:
        res = self.client.get("/api/v1/library/graph")
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
