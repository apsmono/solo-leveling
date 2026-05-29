"""Telegram bot webhook handler."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------
_PROCESSED_PATH: Path = Path("data/telegram_processed.json")
_MAX_PROCESSED_SIZE: int = 1000


def _load_processed_ids() -> set[int]:
    if not _PROCESSED_PATH.exists():
        return set()
    try:
        data = json.loads(_PROCESSED_PATH.read_text(encoding="utf-8"))
        return set(data.get("update_ids", []))
    except (json.JSONDecodeError, OSError):
        logger.warning("Failed to load telegram_processed.json, starting fresh.")
        return set()


def _save_processed_id(update_id: int) -> None:
    ids = list(_load_processed_ids())
    ids.append(update_id)
    # Keep only last _MAX_PROCESSED_SIZE
    ids = ids[-_MAX_PROCESSED_SIZE:]
    _PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    _PROCESSED_PATH.write_text(
        json.dumps({"update_ids": ids, "max_size": _MAX_PROCESSED_SIZE}, indent=2),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Chat storage
# ---------------------------------------------------------------------------
_CHATS_PATH: Path = Path("data/telegram_chats.json")


def _load_chats() -> list[dict[str, Any]]:
    if not _CHATS_PATH.exists():
        return []
    try:
        data = json.loads(_CHATS_PATH.read_text(encoding="utf-8"))
        return list(data.get("chats", []))
    except (json.JSONDecodeError, OSError):
        logger.warning("Failed to load telegram_chats.json, starting fresh.")
        return []


def _save_chat(chat_id: int) -> None:
    chats = _load_chats()
    now = datetime.now(timezone.utc).isoformat()
    for chat in chats:
        if chat.get("chat_id") == chat_id:
            chat["last_seen"] = now
            break
    else:
        chats.append({"chat_id": chat_id, "first_seen": now, "last_seen": now})
    _CHATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CHATS_PATH.write_text(json.dumps({"chats": chats}, indent=2), encoding="utf-8")


def get_stored_chat_ids() -> list[int]:
    """Return list of stored Telegram chat IDs."""
    return [c["chat_id"] for c in _load_chats() if "chat_id" in c]


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
        app.add_handler(CommandHandler("help", _handle_help))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_text))
        _application = app
    return _application


async def _handle_start(update: Any, _: Any) -> None:
    if update.effective_message:
        await update.effective_message.reply_text("Brain online. Send any command or type /help.")


async def _handle_help(update: Any, _: Any) -> None:
    from src.core.router import _handle_help as get_help_text

    text = get_help_text("")
    if update.effective_message:
        await update.effective_message.reply_text(text[:4096])


async def _handle_text(update: Any, _: Any) -> None:
    if not update.effective_message or not update.effective_message.text:
        return
    text = update.effective_message.text.strip()
    from src.core.router import route_command

    reply = route_command(text, source="telegram")

    # Split long replies into chunks
    chunks = _split_reply(reply)
    for chunk in chunks:
        await update.effective_message.reply_text(chunk)


def _split_reply(text: str, max_len: int = 4096) -> list[str]:
    """Split text into chunks that fit Telegram's message limit."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    # Try splitting on double newlines (paragraphs) first
    paragraphs = text.split("\n\n")
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_len:
            current = f"{current}\n\n{para}".strip() if current else para
        else:
            if current:
                chunks.append(current)
            # If a single paragraph is too long, split it further
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


async def process_update(payload: dict[str, Any]) -> None:
    """Process an incoming Telegram webhook update."""
    update_id = payload.get("update_id")
    if update_id is not None:
        if update_id in _load_processed_ids():
            logger.debug("Skipping duplicate update_id: %s", update_id)
            return
        _save_processed_id(update_id)

    app = _ensure_application()
    from telegram import Update

    update = Update.de_json(payload, app.bot)

    # Store chat ID for proactive messaging
    if update.effective_chat and update.effective_chat.id:
        chat_id = update.effective_chat.id
        if isinstance(chat_id, int):
            _save_chat(chat_id)

    await app.process_update(update)
