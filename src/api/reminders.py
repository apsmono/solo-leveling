"""Reminder CRUD REST endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends

from src.api.deps import require_auth
from src.core.config import USE_FIRESTORE_REMINDERS
from src.core.scheduler import create_reminder, format_pending_reminders

router = APIRouter()


@router.get("/reminders")
async def list_reminders(_: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    return {"pending": format_pending_reminders()}


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
    if not USE_FIRESTORE_REMINDERS:
        return {"status": "error", "reply": "Reminder deletion requires Firestore."}
    from src.integrations.firebase.firestore import _client
    _client().collection("reminders").document(reminder_id).delete()
    return {"status": "ok", "id": reminder_id}
