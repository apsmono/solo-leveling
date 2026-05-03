"""Telegram bot webhook handler."""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_BOT_TOKEN: str | None = None
_application: Any | None = None


def _bot_token() -> str:
    global _BOT_TOKEN
    if _BOT_TOKEN is None:
        _BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not _BOT_TOKEN:
            raise EnvironmentError("TELEGRAM_BOT_TOKEN is not set.")
    return _BOT_TOKEN


def _ensure_application() -> Any:
    global _application
    if _application is None:
        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, MessageHandler, filters
        except ModuleNotFoundError as exc:
            raise EnvironmentError("python-telegram-bot is not installed.") from exc

        app = Application.builder().token(_bot_token()).build()
        app.add_handler(CommandHandler("start", _handle_start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_text))
        _application = app
    return _application


async def _handle_start(update: Any, _: Any) -> None:
    if update.effective_message:
        await update.effective_message.reply_text("Brain online. Send any command or type /help.")


async def _handle_text(update: Any, _: Any) -> None:
    if not update.effective_message or not update.effective_message.text:
        return
    text = update.effective_message.text.strip()
    from src.core.router import route_command

    reply = route_command(text, source="telegram")
    await update.effective_message.reply_text(reply[:4096])


async def process_update(payload: dict[str, Any]) -> None:
    """Process an incoming Telegram webhook update."""
    app = _ensure_application()
    from telegram import Update

    update = Update.de_json(payload, app.bot)
    await app.process_update(update)
