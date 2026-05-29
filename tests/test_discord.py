"""Unit tests for Discord bot integration."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Mock discord.py before any imports that depend on it
_mock_discord = MagicMock()
_mock_discord.Intents = MagicMock()
_mock_discord.Intents.default = MagicMock(return_value=MagicMock())
_mock_discord.Embed = MagicMock(return_value=MagicMock())
_mock_discord.AppCommandOptionType = MagicMock()
_mock_discord.AppCommandOptionType.string = 3
_mock_discord.commands = MagicMock()
_mock_discord.ext = MagicMock()
_mock_discord.ext.commands = MagicMock()
_mock_discord.ext.commands.Bot = MagicMock()
sys.modules["discord"] = _mock_discord
sys.modules["discord.ext"] = _mock_discord.ext
sys.modules["discord.ext.commands"] = _mock_discord.ext.commands

from src.integrations.discord.bot import (
    BrainBot,
    _split_hard,
    _split_reply,
    start_bot,
    stop_bot,
)
from src.integrations.discord.client import _split_text, broadcast, send_message
from src.integrations.discord.webhook import _load_chats, _save_chat, get_stored_channel_ids


class DiscordWebhookStorageTests(unittest.TestCase):
    def test_load_chats_missing_file(self) -> None:
        with patch("src.integrations.discord.webhook._CHATS_PATH", Path("/nonexistent/discord_chats.json")):
            chats = _load_chats()
        self.assertEqual(chats, [])

    def test_load_chats_corrupted_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
            f.write("not json")
            temp_path = f.name
        with patch("src.integrations.discord.webhook._CHATS_PATH", Path(temp_path)):
            chats = _load_chats()
        self.assertEqual(chats, [])
        os.unlink(temp_path)

    def test_save_and_load_chat(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
            f.write('{"chats": []}')
            temp_path = f.name
        with patch("src.integrations.discord.webhook._CHATS_PATH", Path(temp_path)):
            _save_chat(channel_id=123456, user_id=789012)
            chats = _load_chats()
        self.assertEqual(len(chats), 1)
        self.assertEqual(chats[0]["channel_id"], 123456)
        self.assertEqual(chats[0]["user_id"], 789012)
        os.unlink(temp_path)

    def test_get_stored_channel_ids(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
            f.write('{"chats": [{"channel_id": 111}, {"channel_id": 222}]}')
            temp_path = f.name
        with patch("src.integrations.discord.webhook._CHATS_PATH", Path(temp_path)):
            ids = get_stored_channel_ids()
        self.assertEqual(ids, [111, 222])
        os.unlink(temp_path)


class DiscordReplySplittingTests(unittest.TestCase):
    def test_split_reply_short(self) -> None:
        text = "Hello world"
        chunks = _split_reply(text, max_len=100)
        self.assertEqual(chunks, ["Hello world"])

    def test_split_reply_long(self) -> None:
        text = "A" * 5000
        chunks = _split_reply(text, max_len=4096)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 4096)
        self.assertEqual(len(chunks[1]), 904)

    def test_split_hard(self) -> None:
        text = "ABCDEFGHIJ"
        chunks = _split_hard(text, max_len=3)
        self.assertEqual(chunks, ["ABC", "DEF", "GHI", "J"])

    def test_split_text(self) -> None:
        text = "A" * 2500
        chunks = _split_text(text, max_len=2000)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 2000)
        self.assertEqual(len(chunks[1]), 500)


class DiscordBotLifecycleTests(unittest.TestCase):
    @patch("src.integrations.discord.bot.os.environ.get", return_value="")
    def test_start_bot_no_token(self, mock_env: MagicMock) -> None:
        import asyncio
        result = asyncio.run(start_bot())
        self.assertIsNone(result)  # Gracefully skips when no token

    def test_stop_bot_not_running(self) -> None:
        import asyncio
        result = asyncio.run(stop_bot())
        self.assertIsNone(result)  # Gracefully skips when no bot


class DiscordClientTests(unittest.TestCase):
    @patch("src.integrations.discord.client._get_bot")
    def test_send_message_success(self, mock_get_bot: MagicMock) -> None:
        mock_channel = MagicMock()
        mock_channel.send = AsyncMock()

        mock_bot = MagicMock()
        mock_bot.get_channel = MagicMock(return_value=mock_channel)
        mock_get_bot.return_value = mock_bot

        import asyncio
        result = asyncio.run(send_message(123456, "Hello!"))
        self.assertTrue(result)
        mock_channel.send.assert_called_once_with("Hello!")

    @patch("src.integrations.discord.client._get_bot")
    def test_send_message_channel_not_found(self, mock_get_bot: MagicMock) -> None:
        mock_bot = MagicMock()
        mock_bot.get_channel = MagicMock(return_value=None)
        mock_get_bot.return_value = mock_bot

        import asyncio
        result = asyncio.run(send_message(123456, "Hello!"))
        self.assertFalse(result)

    @patch("src.integrations.discord.client._get_bot")
    def test_send_message_splits_long_text(self, mock_get_bot: MagicMock) -> None:
        mock_channel = MagicMock()
        mock_channel.send = AsyncMock()

        mock_bot = MagicMock()
        mock_bot.get_channel = MagicMock(return_value=mock_channel)
        mock_get_bot.return_value = mock_bot

        long_text = "A" * 2500
        import asyncio
        result = asyncio.run(send_message(123456, long_text))
        self.assertTrue(result)
        self.assertEqual(mock_channel.send.call_count, 2)

    @patch("src.integrations.discord.client.get_stored_channel_ids")
    @patch("src.integrations.discord.client._get_bot")
    def test_broadcast(self, mock_get_bot: MagicMock, mock_get_chats: MagicMock) -> None:
        mock_channel = MagicMock()
        mock_channel.send = AsyncMock()

        mock_bot = MagicMock()
        mock_bot.get_channel = MagicMock(return_value=mock_channel)
        mock_get_bot.return_value = mock_bot
        mock_get_chats.return_value = [111, 222]

        import asyncio
        results = asyncio.run(broadcast("Hello all!"))
        self.assertEqual(results, {111: True, 222: True})
        self.assertEqual(mock_channel.send.call_count, 2)

    @patch("src.integrations.discord.client.get_stored_channel_ids")
    def test_broadcast_no_channels(self, mock_get_chats: MagicMock) -> None:
        mock_get_chats.return_value = []

        import asyncio
        results = asyncio.run(broadcast("Hello!"))
        self.assertEqual(results, {})


if __name__ == "__main__":
    unittest.main()
