"""Reminder CRUD REST endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends

from src.api.deps import require_auth
from src.core.scheduler import (
    create_reminder,
    delete_pending_reminder,
    format_pending_reminders,
    list_pending_reminders_structured,
)

router = APIRouter()


@router.get("/reminders")
async def list_reminders(_: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    return {
        "pending": format_pending_reminders(),
        "items": list_pending_reminders_structured(),
    }


@router.post("/reminders")
async def add_reminder(
    payload: dict[str, str],
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    message = payload.get("message", "").strip()
    run_at_str = payload.get("run_at", "").strip()
    if not message or not run_at_str:
        return {"status": "error", "reply": "Missing 'message' or 'run_at'."}
    try:
        run_at = datetime.fromisoformat(run_at_str)
    except ValueError:
        return {"status": "error", "reply": "Invalid 'run_at' format. Use ISO format."}
    reminder = create_reminder(message=message, run_at=run_at)
    return {"status": "ok", "reminder": reminder}


@router.delete("/reminders/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, str]:
    if not reminder_id.strip():
        return {"status": "error", "reply": "Missing reminder id."}
    removed = delete_pending_reminder(reminder_id.strip())
    if not removed:
        return {"status": "error", "reply": "Reminder not found or already sent."}
    return {"status": "ok", "id": reminder_id}
