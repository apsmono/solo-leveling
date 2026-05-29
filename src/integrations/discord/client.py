"""Discord proactive messaging client.

Send unprompted messages to stored Discord channels.
"""

from __future__ import annotations

import logging
from typing import Any

from src.integrations.discord.webhook import get_stored_channel_ids

logger = logging.getLogger(__name__)

_MAX_MESSAGE_LENGTH: int = 2000


def _get_bot() -> Any:
    from src.integrations.discord.bot import get_bot
    bot = get_bot()
    if bot is None:
        raise EnvironmentError("Discord bot is not running.")
    return bot


async def send_message(channel_id: int, text: str) -> bool:
    """Send a message to a specific Discord channel.

    Args:
        channel_id: The Discord channel ID to send to.
        text: Message text. Long text is split into multiple messages.

    Returns:
        True if all chunks sent successfully, False otherwise.
    """
    try:
        bot = _get_bot()
    except EnvironmentError:
        logger.error("Cannot send message: Discord bot not running.")
        return False

    channel = bot.get_channel(channel_id)
    if channel is None:
        logger.error("Discord channel %s not found or bot lacks access.", channel_id)
        return False

    chunks = _split_text(text)
    success = True
    for chunk in chunks:
        try:
            await channel.send(chunk)
        except Exception:
            logger.exception("Failed to send message to Discord channel %s", channel_id)
            success = False
    return success


async def broadcast(text: str) -> dict[int, bool]:
    """Send a message to all stored Discord channels.

    Returns:
        Mapping of channel_id -> success bool.
    """
    channel_ids = get_stored_channel_ids()
    if not channel_ids:
        logger.warning("No stored Discord channel IDs to broadcast to.")
        return {}

    results: dict[int, bool] = {}
    for channel_id in channel_ids:
        results[channel_id] = await send_message(channel_id, text)
    return results


def _split_text(text: str, max_len: int = _MAX_MESSAGE_LENGTH) -> list[str]:
    if len(text) <= max_len:
        return [text]
    return [text[i : i + max_len] for i in range(0, len(text), max_len)]
