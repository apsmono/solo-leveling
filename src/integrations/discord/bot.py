"""Discord bot integration for the brain.

Runs as a background task inside the FastAPI lifespan. Uses slash commands
with the defer pattern to handle slow AI responses without hitting Discord's
3-second interaction timeout.

Usage:
    await start_bot()   # inside FastAPI lifespan startup
    await stop_bot()    # inside FastAPI lifespan shutdown
"""

from __future__ import annotations

import logging
import os
from typing import Any

from src.integrations.discord.webhook import _save_chat

logger = logging.getLogger(__name__)

_MAX_EMBED_DESCRIPTION: int = 4096

_bot_token_cache: str | None = None
_bot_instance: Any | None = None

# ---------------------------------------------------------------------------
# Optional discord.py import
# ---------------------------------------------------------------------------
try:
    import discord
    from discord import app_commands
    from discord.ext import commands

    _discord_available = True
except ModuleNotFoundError:
    _discord_available = False
    logger.debug("discord.py is not installed; Discord bot will not function.")


if _discord_available:

    class BrainBot(commands.Bot):
        """Discord bot that routes slash commands to the brain core."""

        def __init__(self) -> None:
            intents = discord.Intents.default()
            intents.message_content = True

            super().__init__(
                command_prefix="!",
                intents=intents,
                help_command=None,
            )

        async def on_ready(self) -> None:
            logger.info("Discord bot logged in as %s (id=%s)", self.user, self.user.id)
            try:
                synced = await self.tree.sync()
                logger.info("Synced %s global slash command(s)", len(synced))
            except Exception:
                logger.exception("Failed to sync Discord slash commands")

        async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
            logger.exception("Discord error in %s", event_method)

        async def setup_hook(self) -> None:
            """Register slash commands."""
            self.tree.add_command(_BrainCommand())
            self.tree.add_command(_StatusCommand())
            self.tree.add_command(_HelpCommand())

    class _BrainCommand(app_commands.Command):
        """/brain <command> — Send any text command to the AI brain."""

        def __init__(self) -> None:
            super().__init__(
                name="brain",
                description="Send a command to your AI brain",
                callback=self._callback,
            )

        async def _callback(self, interaction: discord.Interaction, command: str) -> None:
            await interaction.response.defer(thinking=True)

            from src.core.router import route_command

            reply = route_command(command, source="discord")

            if interaction.channel_id is not None:
                _save_chat(
                    channel_id=interaction.channel_id,
                    user_id=interaction.user.id,
                )

            await _send_reply(interaction, reply)

    class _StatusCommand(app_commands.Command):
        """/status — Quick health check."""

        def __init__(self) -> None:
            super().__init__(
                name="status",
                description="Check if the brain is online",
                callback=self._callback,
            )

        async def _callback(self, interaction: discord.Interaction) -> None:
            await interaction.response.defer(thinking=True)

            from src.core.router import route_command

            reply = route_command("status", source="discord")

            if interaction.channel_id is not None:
                _save_chat(
                    channel_id=interaction.channel_id,
                    user_id=interaction.user.id,
                )

            embed = discord.Embed(
                title="Brain Status",
                description=reply,
                color=0x5865F2,
            )
            await interaction.edit_original_response(embed=embed)

    class _HelpCommand(app_commands.Command):
        """/help — Show available commands."""

        def __init__(self) -> None:
            super().__init__(
                name="help",
                description="Show available brain commands",
                callback=self._callback,
            )

        async def _callback(self, interaction: discord.Interaction) -> None:
            await interaction.response.defer(thinking=True)

            from src.core.router import _handle_help

            reply = _handle_help("")

            if interaction.channel_id is not None:
                _save_chat(
                    channel_id=interaction.channel_id,
                    user_id=interaction.user.id,
                )

            embed = discord.Embed(
                title="Brain Commands",
                description=reply[:_MAX_EMBED_DESCRIPTION],
                color=0x57F287,
            )
            await interaction.edit_original_response(embed=embed)

    async def _send_reply(interaction: Any, reply: str) -> None:
        """Send a brain reply as one or more Discord embeds/messages."""
        chunks = _split_reply(reply)
        if not chunks:
            chunks = ["(no response)"]

        embed = discord.Embed(
            title="Brain Response",
            description=chunks[0],
            color=0x00FF00,
        )
        await interaction.edit_original_response(embed=embed)

        for chunk in chunks[1:]:
            await interaction.followup.send(chunk)

else:
    # Dummy BrainBot for type-checking when discord.py is not installed
    BrainBot = Any  # type: ignore[misc,assignment]

    async def _send_reply(interaction: Any, reply: str) -> None:  # type: ignore[misc]
        pass


def _split_reply(text: str, max_len: int = _MAX_EMBED_DESCRIPTION) -> list[str]:
    """Split text into chunks that fit Discord embed limits."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_len:
            current = f"{current}\n\n{para}".strip() if current else para
        else:
            if current:
                chunks.append(current)
            if len(para) > max_len:
                chunks.extend(_split_hard(para, max_len))
            else:
                current = para
    if current:
        chunks.append(current)
    return chunks


def _split_hard(text: str, max_len: int) -> list[str]:
    """Hard-split text at max_len boundaries."""
    return [text[i : i + max_len] for i in range(0, len(text), max_len)]


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

def _bot_token() -> str:
    global _bot_token_cache
    if _bot_token_cache is None:
        _bot_token_cache = os.environ.get("DISCORD_BOT_TOKEN")
        if not _bot_token_cache:
            raise EnvironmentError("DISCORD_BOT_TOKEN is not set.")
    return _bot_token_cache


async def start_bot() -> None:
    """Start the Discord bot as a background task.

    Called from FastAPI lifespan startup. The bot connects to Discord's
    gateway and runs until stop_bot() is called.
    """
    if not _discord_available:
        logger.info("discord.py is not installed; Discord bot will not start.")
        return

    token = os.environ.get("DISCORD_BOT_TOKEN", "")
    if not token:
        logger.info("DISCORD_BOT_TOKEN not set; Discord bot will not start.")
        return

    global _bot_instance
    if _bot_instance is not None:
        logger.warning("Discord bot already running.")
        return

    _bot_instance = BrainBot()
    import asyncio

    asyncio.create_task(_run_bot(token))
    logger.info("Discord bot startup task created.")


async def _run_bot(token: str) -> None:
    """Internal: run the bot until disconnected."""
    global _bot_instance
    try:
        await _bot_instance.start(token)
    except Exception:
        logger.exception("Discord bot crashed")
        _bot_instance = None


async def stop_bot() -> None:
    """Gracefully stop the Discord bot.

    Called from FastAPI lifespan shutdown.
    """
    global _bot_instance
    if _bot_instance is None:
        return

    logger.info("Shutting down Discord bot...")
    try:
        await _bot_instance.close()
    except Exception:
        logger.exception("Error shutting down Discord bot")
    finally:
        _bot_instance = None
        logger.info("Discord bot stopped.")


def get_bot() -> Any | None:
    """Return the running bot instance, or None if not started."""
    return _bot_instance
