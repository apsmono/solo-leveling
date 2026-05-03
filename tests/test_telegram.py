"""Unit tests for Telegram webhook integration."""

from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

_mock_telegram = MagicMock()
sys.modules["telegram"] = _mock_telegram
sys.modules["telegram.ext"] = _mock_telegram.ext

from src.app import app


class TelegramWebhookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        _mock_telegram.ext.Application.builder.return_value.token.return_value.build.reset_mock()

    @patch("src.integrations.telegram.webhook._ensure_application")
    @patch("src.core.router.route_command", return_value="Brain is online and listening.")
    def test_webhook_text_message(self, mock_route: MagicMock, mock_ensure: MagicMock) -> None:
        from unittest.mock import AsyncMock
        mock_app = MagicMock()
        mock_app.process_update = AsyncMock()
        mock_ensure.return_value = mock_app
        response = self.client.post("/webhook/telegram", json={"update_id": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_webhook_no_secret_required(self) -> None:
        from unittest.mock import AsyncMock
        with patch("src.integrations.telegram.webhook._ensure_application") as mock_ensure:
            mock_app = MagicMock()
            mock_app.process_update = AsyncMock()
            mock_ensure.return_value = mock_app
            response = self.client.post("/webhook/telegram", json={"update_id": 1})
        self.assertEqual(response.status_code, 200)

    @patch("src.core.config.TELEGRAM_WEBHOOK_SECRET", "secret123")
    def test_webhook_invalid_secret(self) -> None:
        response = self.client.post("/webhook/telegram", json={"update_id": 1, "secret": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @patch("src.core.config.TELEGRAM_WEBHOOK_SECRET", "secret123")
    @patch("src.integrations.telegram.webhook._ensure_application")
    def test_webhook_valid_secret(self, mock_ensure: MagicMock) -> None:
        from unittest.mock import AsyncMock
        mock_app = MagicMock()
        mock_app.process_update = AsyncMock()
        mock_ensure.return_value = mock_app
        response = self.client.post("/webhook/telegram", json={"update_id": 1, "secret": "secret123"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
