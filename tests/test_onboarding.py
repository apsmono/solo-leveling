"""
Tests for Phase 5: Onboarding — profile and identity endpoints.

Endpoints tested:
- GET  /api/v1/profile                    — first-run detection
- POST /api/v1/profile                    — save profile
- POST /api/v1/onboarding/parse-identity  — LLM profile parsing
- POST /api/v1/profile/onboarding-step    — step progress tracking

All tests run offline (mocked auth + dependencies).
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app import app


class OnboardingAPITests(unittest.TestCase):
    """Contract tests for onboarding + profile endpoints."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}

    # --- GET /profile ---

    @patch("src.api.deps.verify_id_token")
    def test_get_profile_404_when_none(self, mock_verify: MagicMock) -> None:
        """GET /api/v1/profile returns 404 when no profile exists."""
        mock_verify.return_value = self.mock_user
        with patch("src.api.profile.load_profile", return_value=None):
            response = self.client.get(
                "/api/v1/profile",
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 404)

    @patch("src.api.deps.verify_id_token")
    def test_get_profile_returns_existing(self, mock_verify: MagicMock) -> None:
        """GET /api/v1/profile returns 200 + profile when it exists."""
        mock_verify.return_value = self.mock_user
        mock_profile = {"role": "Engineer", "pain_points": [], "suggested_apps": []}
        with patch("src.api.profile.load_profile", return_value=mock_profile):
            response = self.client.get(
                "/api/v1/profile",
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["profile"]["role"], "Engineer")

    # --- POST /profile ---

    @patch("src.api.deps.verify_id_token")
    def test_post_profile_saves(self, mock_verify: MagicMock) -> None:
        """POST /api/v1/profile saves profile and returns 200."""
        mock_verify.return_value = self.mock_user
        payload = {"role": "Designer", "pain_points": ["too many meetings"]}
        with patch("src.api.profile.save_profile") as mock_save:
            response = self.client.post(
                "/api/v1/profile",
                json=payload,
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["profile"]["role"], "Designer")
        mock_save.assert_called_once()

    # --- POST /onboarding/parse-identity ---

    @patch("src.api.deps.verify_id_token")
    def test_parse_identity_returns_profile(self, mock_verify: MagicMock) -> None:
        """POST /api/v1/onboarding/parse-identity with text returns 200 + profile."""
        mock_verify.return_value = self.mock_user
        mock_profile = {
            "role": "Software engineer",
            "pain_points": ["too many emails"],
            "suggested_apps": ["gmail"],
            "context_templates": [],
            "needs_followup": False,
            "followup_question": "",
        }
        with patch("src.api.onboarding.parse_identity", return_value=mock_profile):
            response = self.client.post(
                "/api/v1/onboarding/parse-identity",
                json={"text": "I'm a software engineer drowning in emails"},
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("profile", data)
        self.assertEqual(data["profile"]["role"], "Software engineer")

    @patch("src.api.deps.verify_id_token")
    def test_parse_identity_missing_text_returns_400(self, mock_verify: MagicMock) -> None:
        """POST /api/v1/onboarding/parse-identity with empty body returns 400."""
        mock_verify.return_value = self.mock_user
        response = self.client.post(
            "/api/v1/onboarding/parse-identity",
            json={},
            headers={"Authorization": "Bearer valid-token"},
        )
        self.assertEqual(response.status_code, 400)

    @patch("src.api.deps.verify_id_token")
    def test_parse_identity_needs_followup(self, mock_verify: MagicMock) -> None:
        """POST /api/v1/onboarding/parse-identity with vague text returns needs_followup=true."""
        mock_verify.return_value = self.mock_user
        mock_profile = {
            "role": "",
            "pain_points": [],
            "suggested_apps": [],
            "context_templates": [],
            "needs_followup": True,
            "followup_question": "Could you tell me a bit more about what you do and which apps you use most?",
        }
        with patch("src.api.onboarding.parse_identity", return_value=mock_profile):
            response = self.client.post(
                "/api/v1/onboarding/parse-identity",
                json={"text": "I work in tech"},
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["profile"]["needs_followup"])
        self.assertIn("followup_question", data["profile"])

    # --- POST /profile/onboarding-step ---

    @patch("src.api.deps.verify_id_token")
    def test_onboarding_step_saves(self, mock_verify: MagicMock) -> None:
        """POST /api/v1/profile/onboarding-step with step 2 returns 200."""
        mock_verify.return_value = self.mock_user
        with patch("src.api.onboarding.save_onboarding_step") as mock_save:
            response = self.client.post(
                "/api/v1/profile/onboarding-step",
                json={"step": 2},
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        mock_save.assert_called_once_with(2)

    # --- Auth requirement ---

    @patch("src.api.deps.verify_id_token")
    def test_all_endpoints_require_auth(self, mock_verify: MagicMock) -> None:
        """All endpoints return 401 when no Authorization header is provided."""
        mock_verify.side_effect = Exception("No token")
        endpoints = [
            ("GET", "/api/v1/profile"),
            ("POST", "/api/v1/profile"),
            ("POST", "/api/v1/onboarding/parse-identity"),
            ("POST", "/api/v1/profile/onboarding-step"),
        ]
        for method, path in endpoints:
            if method == "GET":
                resp = self.client.get(path)
            else:
                resp = self.client.post(path, json={"text": "test", "step": 1})
            self.assertIn(
                resp.status_code,
                (401, 403),
                f"{method} {path} should require auth, got {resp.status_code}",
            )


if __name__ == "__main__":
    unittest.main()
