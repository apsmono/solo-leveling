"""CLI for managing Telegram bot webhook.

Usage:
    python -m src.integrations.telegram.cli set <url>
    python -m src.integrations.telegram.cli info
    python -m src.integrations.telegram.cli delete
    python -m src.integrations.telegram.cli poll
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from typing import Any

from src.integrations.telegram.webhook import _bot_token
from src.integrations.telegram.webhook import process_update

logger = logging.getLogger(__name__)


def _get_bot() -> Any:
    try:
        from telegram import Bot
    except ModuleNotFoundError as exc:
        raise EnvironmentError("python-telegram-bot is not installed. Run: pip install python-telegram-bot") from exc
    return Bot(token=_bot_token())


async def cmd_set(url: str) -> int:
    """Register webhook URL with Telegram."""
    from src.core.config import TELEGRAM_WEBHOOK_SECRET

    bot = _get_bot()
    kwargs: dict[str, Any] = {"url": url, "drop_pending_updates": True}
    if TELEGRAM_WEBHOOK_SECRET:
        kwargs["secret_token"] = TELEGRAM_WEBHOOK_SECRET

    result = await bot.set_webhook(**kwargs)
    if result:
        print(f"Webhook set: {url}")
        if TELEGRAM_WEBHOOK_SECRET:
            print("Secret token configured.")
    else:
        print("Failed to set webhook.", file=sys.stderr)
        return 1
    return 0


async def cmd_info() -> int:
    """Show current webhook info."""
    bot = _get_bot()
    info = await bot.get_webhook_info()
    print(f"URL:         {info.url or '(not set)'}")
    print(f"Pending:     {info.pending_update_count}")
    print(f"Max conn:    {info.max_connections}")
    if info.last_error_date:
        print(f"Last error:  {info.last_error_date} — {info.last_error_message}")
    return 0


async def cmd_delete() -> int:
    """Delete webhook and drop pending updates."""
    bot = _get_bot()
    result = await bot.delete_webhook(drop_pending_updates=True)
    if result:
        print("Webhook deleted.")
    else:
        print("Failed to delete webhook.", file=sys.stderr)
        return 1
    return 0


async def cmd_poll() -> int:
    """Start polling mode for local development."""
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
    except ModuleNotFoundError as exc:
        raise EnvironmentError("python-telegram-bot is not installed.") from exc

    app = Application.builder().token(_bot_token()).build()

    # Re-use handlers from webhook module
    from src.integrations.telegram.webhook import _handle_start, _handle_help, _handle_text
    app.add_handler(CommandHandler("start", _handle_start))
    app.add_handler(CommandHandler("help", _handle_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_text))

    print("Starting polling mode... Press Ctrl+C to stop.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    try:
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
    return 0


async def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage Telegram bot webhook")
    subparsers = parser.add_subparsers(dest="command", required=True)

    set_parser = subparsers.add_parser("set", help="Set webhook URL")
    set_parser.add_argument("url", help="Full webhook URL (e.g. https://example.com/webhook/telegram)")

    subparsers.add_parser("info", help="Show webhook info")
    subparsers.add_parser("delete", help="Delete webhook")
    subparsers.add_parser("poll", help="Start polling mode (local dev)")

    args = parser.parse_args(argv)

    if args.command == "set":
        return await cmd_set(args.url)
    if args.command == "info":
        return await cmd_info()
    if args.command == "delete":
        return await cmd_delete()
    if args.command == "poll":
        return await cmd_poll()
    return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        sys.exit(asyncio.run(main()))
    except EnvironmentError as e:
        logger.error("%s", e)
        sys.exit(1)
