"""Tests for GitHub cross-repo integration."""

from __future__ import annotations

import json
import os
import unittest
from unittest.mock import MagicMock, patch

from src.core.router import route_command


class GitHubClientTests(unittest.TestCase):
    """Unit tests for src/integrations/github/client.py"""

    @patch("src.integrations.github.client.GITHUB_PAT", "")
    def test_health_check_missing_pat(self) -> None:
        from src.integrations.github import client as gh
        result = gh.health_check()
        self.assertFalse(result["ok"])
        self.assertIn("GITHUB_PAT", result["error"])

    @patch("src.integrations.github.client.GITHUB_PAT", "test-token")
    @patch("src.integrations.github.client._request")
    def test_health_check_success(self, mock_req: MagicMock) -> None:
        from src.integrations.github import client as gh
        mock_req.return_value = {"login": "testuser"}
        result = gh.health_check()
        self.assertTrue(result["ok"])
        self.assertEqual(result["user"], "testuser")

    @patch.dict(os.environ, {"GITHUB_PAT": "test-token"}, clear=False)
    @patch("src.integrations.github.client._request")
    def test_list_repos(self, mock_req: MagicMock) -> None:
        from src.integrations.github import client as gh
        mock_req.return_value = [
            {
                "full_name": "apsmono/solo-leveling",
                "html_url": "https://github.com/apsmono/solo-leveling",
                "private": True,
                "updated_at": "2026-05-01T00:00:00Z",
            }
        ]
        repos = gh.list_repos()
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]["name"], "apsmono/solo-leveling")
        self.assertTrue(repos[0]["private"])

    @patch.dict(os.environ, {"GITHUB_PAT": "test-token"}, clear=False)
    @patch("src.integrations.github.client._request")
    def test_create_issue(self, mock_req: MagicMock) -> None:
        from src.integrations.github import client as gh
        mock_req.return_value = {
            "number": 42,
            "title": "Fix header",
            "html_url": "https://github.com/apsmono/repo/issues/42",
            "state": "open",
        }
        issue = gh.create_issue("apsmono/repo", "Fix header", "The header is misaligned.")
        self.assertEqual(issue["number"], 42)
        self.assertEqual(issue["title"], "Fix header")

    @patch.dict(os.environ, {"GITHUB_PAT": "test-token"}, clear=False)
    @patch("src.integrations.github.client._request")
    def test_trigger_workflow(self, mock_req: MagicMock) -> None:
        from src.integrations.github import client as gh
        mock_req.return_value = {}
        result = gh.trigger_workflow("apsmono/repo", "deploy.yml", branch="main")
        self.assertEqual(result["status"], "triggered")
        self.assertEqual(result["workflow"], "deploy.yml")


class GitHubRouterTests(unittest.TestCase):
    """Tests for GitHub command routing."""

    @patch("src.integrations.github.client.health_check")
    @patch("src.integrations.github.client.list_repos")
    def test_github_list_repos(self, mock_list: MagicMock, mock_health: MagicMock) -> None:
        mock_health.return_value = {"ok": True, "user": "apsmono"}
        mock_list.return_value = [
            {"name": "apsmono/repo1", "private": False, "url": "https://github.com/apsmono/repo1"},
            {"name": "apsmono/repo2", "private": True, "url": "https://github.com/apsmono/repo2"},
        ]
        reply = route_command("github list repos")
        self.assertIn("repo1", reply)
        self.assertIn("repo2", reply)

    @patch("src.integrations.github.client.health_check")
    def test_github_list_repos_no_pat(self, mock_health: MagicMock) -> None:
        mock_health.return_value = {"ok": False, "error": "GITHUB_PAT not configured"}
        reply = route_command("list my repos")
        self.assertIn("unavailable", reply.lower())

    @patch("src.integrations.github.client.health_check")
    @patch("src.integrations.github.client.create_issue")
    def test_github_create_issue(self, mock_create: MagicMock, mock_health: MagicMock) -> None:
        mock_health.return_value = {"ok": True, "user": "apsmono"}
        mock_create.return_value = {"number": 7, "title": "Bug", "url": "https://github.com/apsmono/x/issues/7"}
        reply = route_command("github create issue in apsmono/x: Bug")
        self.assertIn("#7", reply)
        self.assertIn("Bug", reply)

    @patch("src.integrations.github.client.health_check")
    @patch("src.integrations.github.client.trigger_workflow")
    def test_github_trigger_workflow(self, mock_trigger: MagicMock, mock_health: MagicMock) -> None:
        mock_health.return_value = {"ok": True, "user": "apsmono"}
        mock_trigger.return_value = {"status": "triggered", "repo": "apsmono/api", "workflow": "deploy.yml"}
        reply = route_command("github trigger apsmono/api/deploy.yml")
        self.assertIn("triggered", reply.lower())

    @patch("src.integrations.github.client.health_check")
    def test_github_status(self, mock_health: MagicMock) -> None:
        mock_health.return_value = {"ok": True, "user": "apsmono"}
        reply = route_command("github status")
        self.assertIn("healthy", reply.lower())

    @patch("src.integrations.github.client.health_check")
    def test_github_status_unhealthy(self, mock_health: MagicMock) -> None:
        mock_health.return_value = {"ok": False, "error": "bad creds"}
        reply = route_command("github health")
        self.assertIn("unhealthy", reply.lower())


class GitHubIntentDetectionTests(unittest.TestCase):
    """Tests that GitHub commands are routed to the correct intent."""

    def _detect(self, text: str) -> str:
        from src.core.router import _detect_intent
        return _detect_intent(text)

    def test_detect_github_repos(self) -> None:
        self.assertEqual(self._detect("github list repos"), "github_repos")
        self.assertEqual(self._detect("list my repos"), "github_repos")
        self.assertEqual(self._detect("my repos"), "github_repos")

    def test_detect_github_issue(self) -> None:
        self.assertEqual(self._detect("github create issue in apsmono/x: title"), "github_issue")
        self.assertEqual(self._detect("create issue in apsmono/x: title"), "github_issue")

    def test_detect_github_workflow(self) -> None:
        self.assertEqual(self._detect("github trigger apsmono/api/deploy.yml"), "github_workflow")
        self.assertEqual(self._detect("trigger workflow apsmono/api/deploy.yml"), "github_workflow")

    def test_detect_github_status(self) -> None:
        self.assertEqual(self._detect("github status"), "github_status")
        self.assertEqual(self._detect("github health"), "github_status")


if __name__ == "__main__":
    unittest.main()
