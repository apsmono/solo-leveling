"""Telegram proactive messaging client.

Send unprompted messages to stored chat IDs.
"""

from __future__ import annotations

import logging
from typing import Any

from src.integrations.telegram.webhook import _bot_token, get_stored_chat_ids

logger = logging.getLogger(__name__)

_MAX_MESSAGE_LENGTH: int = 4096


def _get_bot() -> Any:
    try:
        from telegram import Bot
    except ModuleNotFoundError as exc:
        raise EnvironmentError("python-telegram-bot is not installed.") from exc
    return Bot(token=_bot_token())


async def send_message(chat_id: int, text: str, parse_mode: str = "") -> bool:
    """Send a message to a specific Telegram chat.

    Args:
        chat_id: The Telegram chat ID to send to.
        text: Message text. Long text is split into multiple messages.
        parse_mode: Optional parse mode ("Markdown", "HTML", or "" for plain).

    Returns:
        True if all chunks sent successfully, False otherwise.
    """
    try:
        bot = _get_bot()
    except EnvironmentError:
        logger.error("Cannot send message: python-telegram-bot not installed.")
        return False

    chunks = _split_text(text)
    success = True
    for chunk in chunks:
        try:
            kwargs: dict[str, Any] = {"chat_id": chat_id, "text": chunk}
            if parse_mode:
                kwargs["parse_mode"] = parse_mode
            await bot.send_message(**kwargs)
        except Exception:
            logger.exception("Failed to send message to chat %s", chat_id)
            success = False
    return success


async def broadcast(text: str, parse_mode: str = "") -> dict[int, bool]:
    """Send a message to all stored chat IDs.

    Returns:
        Mapping of chat_id -> success bool.
    """
    chat_ids = get_stored_chat_ids()
    if not chat_ids:
        logger.warning("No stored chat IDs to broadcast to.")
        return {}

    results: dict[int, bool] = {}
    for chat_id in chat_ids:
        results[chat_id] = await send_message(chat_id, text, parse_mode)
    return results


def _split_text(text: str, max_len: int = _MAX_MESSAGE_LENGTH) -> list[str]:
    if len(text) <= max_len:
        return [text]
    return [text[i : i + max_len] for i in range(0, len(text), max_len)]
