"""Unit tests for Telegram webhook integration."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
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
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
            f.write('{"update_ids": [], "max_size": 1000}')
            temp_path = f.name

        with patch("src.integrations.telegram.webhook._ensure_application") as mock_ensure:
            mock_app = MagicMock()
            mock_app.process_update = AsyncMock()
            mock_ensure.return_value = mock_app
            with patch("src.integrations.telegram.webhook._PROCESSED_PATH", Path(temp_path)):
                response = self.client.post("/webhook/telegram", json={"update_id": 1})
        self.assertEqual(response.status_code, 200)
        mock_app.process_update.assert_called_once()
        os.unlink(temp_path)

    @patch("src.core.config.TELEGRAM_WEBHOOK_SECRET", "secret123")
    def test_webhook_invalid_secret(self) -> None:
        response = self.client.post(
            "/webhook/telegram",
            json={"update_id": 1},
            headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @patch("src.core.config.TELEGRAM_WEBHOOK_SECRET", "secret123")
    @patch("src.integrations.telegram.webhook._ensure_application")
    def test_webhook_valid_secret_header(self, mock_ensure: MagicMock) -> None:
        from unittest.mock import AsyncMock
        mock_app = MagicMock()
        mock_app.process_update = AsyncMock()
        mock_ensure.return_value = mock_app
        response = self.client.post(
            "/webhook/telegram",
            json={"update_id": 1},
            headers={"X-Telegram-Bot-Api-Secret-Token": "secret123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @patch("src.integrations.telegram.webhook._ensure_application")
    def test_webhook_dedup(self, mock_ensure: MagicMock) -> None:
        """Same update_id twice should skip the second."""
        from unittest.mock import AsyncMock
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
            f.write('{"update_ids": [], "max_size": 1000}')
            temp_path = f.name

        mock_app = MagicMock()
        mock_app.process_update = AsyncMock()
        mock_ensure.return_value = mock_app

        # First call
        with patch("src.integrations.telegram.webhook._PROCESSED_PATH", Path(temp_path)):
            response1 = self.client.post("/webhook/telegram", json={"update_id": 999})
        self.assertEqual(response1.status_code, 200)

        # Second call with same update_id — should still return 200 but skip processing
        with patch("src.integrations.telegram.webhook._PROCESSED_PATH", Path(temp_path)):
            response2 = self.client.post("/webhook/telegram", json={"update_id": 999})
        self.assertEqual(response2.status_code, 200)

        # process_update should only be called once
        self.assertEqual(mock_app.process_update.call_count, 1)

        os.unlink(temp_path)

    @patch("src.integrations.telegram.webhook._ensure_application")
    def test_webhook_stores_chat_id(self, mock_ensure: MagicMock) -> None:
        """Incoming message should persist chat_id."""
        from unittest.mock import AsyncMock
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
            f.write('{"chats": []}')
            temp_path = f.name

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as pf:
            pf.write('{"update_ids": [], "max_size": 1000}')
            processed_path = pf.name

        mock_app = MagicMock()
        mock_app.process_update = AsyncMock()
        mock_ensure.return_value = mock_app

        # Mock Update.de_json to return an object with a real int chat id
        mock_update = MagicMock()
        mock_update.effective_chat = MagicMock()
        mock_update.effective_chat.id = 123456789
        _mock_telegram.Update.de_json.return_value = mock_update

        with patch("src.integrations.telegram.webhook._CHATS_PATH", Path(temp_path)):
            with patch("src.integrations.telegram.webhook._PROCESSED_PATH", Path(processed_path)):
                response = self.client.post(
                    "/webhook/telegram",
                    json={
                        "update_id": 1,
                        "message": {
                            "chat": {"id": 123456789, "type": "private"},
                            "text": "hello",
                            "message_id": 1,
                            "date": 1,
                        },
                    },
                )
        self.assertEqual(response.status_code, 200)

        # Verify chat was stored
        with open(temp_path) as f:
            data = json.loads(f.read())
        self.assertEqual(len(data["chats"]), 1)
        self.assertEqual(data["chats"][0]["chat_id"], 123456789)

        os.unlink(temp_path)
        os.unlink(processed_path)


if __name__ == "__main__":
    unittest.main()
