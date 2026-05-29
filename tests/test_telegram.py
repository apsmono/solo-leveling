"""Unit tests for Telegram webhook integration."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

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


class TelegramClientTests(unittest.TestCase):
    @patch("src.integrations.telegram.client._get_bot")
    def test_send_message_success(self, mock_get_bot: MagicMock) -> None:
        from src.integrations.telegram.client import send_message
        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()
        mock_get_bot.return_value = mock_bot

        import asyncio
        result = asyncio.run(send_message(123456, "Hello!"))
        self.assertTrue(result)
        mock_bot.send_message.assert_called_once_with(chat_id=123456, text="Hello!")

    @patch("src.integrations.telegram.client._get_bot")
    def test_send_message_splits_long_text(self, mock_get_bot: MagicMock) -> None:
        from src.integrations.telegram.client import send_message
        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()
        mock_get_bot.return_value = mock_bot

        long_text = "A" * 5000
        import asyncio
        result = asyncio.run(send_message(123456, long_text))
        self.assertTrue(result)
        self.assertEqual(mock_bot.send_message.call_count, 2)

    @patch("src.integrations.telegram.client.get_stored_chat_ids")
    @patch("src.integrations.telegram.client._get_bot")
    def test_broadcast(self, mock_get_bot: MagicMock, mock_get_chats: MagicMock) -> None:
        from src.integrations.telegram.client import broadcast
        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()
        mock_get_bot.return_value = mock_bot
        mock_get_chats.return_value = [111, 222]

        import asyncio
        results = asyncio.run(broadcast("Hello all!"))
        self.assertEqual(results, {111: True, 222: True})
        self.assertEqual(mock_bot.send_message.call_count, 2)

    @patch("src.integrations.telegram.client.get_stored_chat_ids")
    def test_broadcast_no_chats(self, mock_get_chats: MagicMock) -> None:
        from src.integrations.telegram.client import broadcast
        mock_get_chats.return_value = []

        import asyncio
        results = asyncio.run(broadcast("Hello!"))
        self.assertEqual(results, {})


class TelegramCliTests(unittest.TestCase):
    @patch("src.integrations.telegram.cli._get_bot")
    def test_cli_set(self, mock_get_bot: MagicMock) -> None:
        from src.integrations.telegram.cli import cmd_set
        mock_bot = MagicMock()
        mock_bot.set_webhook = AsyncMock(return_value=True)
        mock_get_bot.return_value = mock_bot

        import asyncio
        result = asyncio.run(cmd_set("https://example.com/webhook/telegram"))
        self.assertEqual(result, 0)
        mock_bot.set_webhook.assert_called_once()
        call_kwargs = mock_bot.set_webhook.call_args.kwargs
        self.assertEqual(call_kwargs["url"], "https://example.com/webhook/telegram")
        self.assertTrue(call_kwargs["drop_pending_updates"])

    @patch("src.integrations.telegram.cli._get_bot")
    def test_cli_info(self, mock_get_bot: MagicMock) -> None:
        from src.integrations.telegram.cli import cmd_info
        mock_info = MagicMock()
        mock_info.url = "https://example.com/webhook/telegram"
        mock_info.pending_update_count = 0
        mock_info.max_connections = 40
        mock_info.last_error_date = None
        mock_info.last_error_message = None

        mock_bot = MagicMock()
        mock_bot.get_webhook_info = AsyncMock(return_value=mock_info)
        mock_get_bot.return_value = mock_bot

        import asyncio
        result = asyncio.run(cmd_info())
        self.assertEqual(result, 0)
        mock_bot.get_webhook_info.assert_called_once()

    @patch("src.integrations.telegram.cli._get_bot")
    def test_cli_delete(self, mock_get_bot: MagicMock) -> None:
        from src.integrations.telegram.cli import cmd_delete
        mock_bot = MagicMock()
        mock_bot.delete_webhook = AsyncMock(return_value=True)
        mock_get_bot.return_value = mock_bot

        import asyncio
        result = asyncio.run(cmd_delete())
        self.assertEqual(result, 0)
        mock_bot.delete_webhook.assert_called_once_with(drop_pending_updates=True)


if __name__ == "__main__":
    unittest.main()
