"""Discord chat storage helpers.

Persist channel/user IDs so the brain can send proactive messages.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Chat storage
# ---------------------------------------------------------------------------
_CHATS_PATH: Path = Path("data/discord_chats.json")


def _load_chats() -> list[dict[str, Any]]:
    if not _CHATS_PATH.exists():
        return []
    try:
        data = json.loads(_CHATS_PATH.read_text(encoding="utf-8"))
        return list(data.get("chats", []))
    except (json.JSONDecodeError, OSError):
        logger.warning("Failed to load discord_chats.json, starting fresh.")
        return []


def _save_chat(channel_id: int, user_id: int | None = None) -> None:
    chats = _load_chats()
    now = datetime.now(timezone.utc).isoformat()
    for chat in chats:
        if chat.get("channel_id") == channel_id:
            chat["last_seen"] = now
            if user_id is not None:
                chat["user_id"] = user_id
            break
    else:
        chat: dict[str, Any] = {
            "channel_id": channel_id,
            "first_seen": now,
            "last_seen": now,
        }
        if user_id is not None:
            chat["user_id"] = user_id
        chats.append(chat)
    _CHATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CHATS_PATH.write_text(json.dumps({"chats": chats}, indent=2), encoding="utf-8")


def get_stored_channel_ids() -> list[int]:
    """Return list of stored Discord channel IDs."""
    return [c["channel_id"] for c in _load_chats() if "channel_id" in c]
