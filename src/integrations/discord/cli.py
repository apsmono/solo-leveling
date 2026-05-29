"""CLI for managing Discord bot slash commands.

Usage:
    python -m src.integrations.discord.cli sync
    python -m src.integrations.discord.cli clear
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from src.core.config import DISCORD_BOT_TOKEN

logger = logging.getLogger(__name__)

try:
    import discord
    from discord.ext import commands

    _discord_available = True
except ModuleNotFoundError:
    _discord_available = False


async def cmd_sync() -> int:
    """Sync slash commands to Discord globally."""
    if not _discord_available:
        print("discord.py is not installed. Run: pip install discord.py>=2.7.0", file=sys.stderr)
        return 1

    if not DISCORD_BOT_TOKEN:
        print("DISCORD_BOT_TOKEN is not set.", file=sys.stderr)
        return 1

    from src.integrations.discord.bot import BrainBot

    bot = BrainBot()

    @bot.event
    async def on_ready() -> None:
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} global slash command(s)")
            for cmd in synced:
                print(f"  - /{cmd.name}")
        except Exception as exc:
            print(f"Failed to sync commands: {exc}", file=sys.stderr)
        finally:
            await bot.close()

    try:
        await bot.start(DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        print("Invalid DISCORD_BOT_TOKEN.", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


async def cmd_clear() -> int:
    """Clear all global slash commands."""
    if not _discord_available:
        print("discord.py is not installed. Run: pip install discord.py>=2.7.0", file=sys.stderr)
        return 1

    if not DISCORD_BOT_TOKEN:
        print("DISCORD_BOT_TOKEN is not set.", file=sys.stderr)
        return 1

    from src.integrations.discord.bot import BrainBot

    bot = BrainBot()

    @bot.event
    async def on_ready() -> None:
        try:
            bot.tree.clear_commands(guild=None)
            await bot.tree.sync()
            print("Cleared all global slash commands.")
        except Exception as exc:
            print(f"Failed to clear commands: {exc}", file=sys.stderr)
        finally:
            await bot.close()

    try:
        await bot.start(DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        print("Invalid DISCORD_BOT_TOKEN.", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


async def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage Discord bot slash commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("sync", help="Sync slash commands to Discord")
    subparsers.add_parser("clear", help="Clear all global slash commands")

    args = parser.parse_args(argv)

    if args.command == "sync":
        return await cmd_sync()
    if args.command == "clear":
        return await cmd_clear()
    return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        sys.exit(asyncio.run(main()))
    except EnvironmentError as e:
        logger.error("%s", e)
        sys.exit(1)
