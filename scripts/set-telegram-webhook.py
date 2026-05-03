#!/usr/bin/env python3
"""Register the Telegram bot webhook URL.

Usage:
    export TELEGRAM_BOT_TOKEN=...
    export WEBHOOK_URL=https://your-domain.com/webhook/telegram
    python scripts/set-telegram-webhook.py
"""

from __future__ import annotations

import asyncio
import os


try:
    from telegram import Bot
except ModuleNotFoundError:
    raise SystemExit("python-telegram-bot is not installed. Run: pip install python-telegram-bot")


async def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    url = os.environ.get("WEBHOOK_URL")
    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")

    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set.")
    if not url:
        raise SystemExit("WEBHOOK_URL is not set.")

    bot = Bot(token)

    # Append secret as query param if configured
    full_url = f"{url}?secret={secret}" if secret else url

    await bot.set_webhook(url=full_url)
    info = await bot.get_webhook_info()
    print(f"Webhook set: {info.url}")
    print(f"Pending updates: {info.pending_update_count}")


if __name__ == "__main__":
    asyncio.run(main())
