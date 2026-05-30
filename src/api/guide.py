"""
AI Guide REST endpoints.

Provides the backend for the persistent AI Guide panel:
- POST /guide/command  — parse intent and return reply
- GET  /guide/status   — return guide metrics
- POST /guide/park     — save a stray thought to library without context switch

All endpoints require Firebase authentication.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import require_auth
from src.core.config import SIGNAL_OWNER_ID
from src.core.libraries import _get_store, handle_library_command
from src.core.router import route_command

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/guide/command")
async def guide_command(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Parse a natural language command and return the routed reply."""
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'text' in request payload.",
        )

    source = f"api:{user.get('email', 'unknown')}"
    reply = route_command(text, source=source)
    return {"status": "ok", "reply": reply}


@router.get("/guide/status")
async def guide_status(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Return guide metrics: library entries, recent captures, commands processed."""
    try:
        store = _get_store()
        index = store.build_index()
        entries = index.get("entries", [])

        # Count total entries
        total_entries = len(entries)

        # Count recent captures (updated or captured within last 24h)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_captures = 0
        for entry in entries:
            updated = entry.get("updated_at") or entry.get("captured_at")
            if updated:
                try:
                    # Handle ISO format with or without timezone
                    if isinstance(updated, str):
                        if updated.endswith("Z"):
                            updated = updated[:-1] + "+00:00"
                        dt = datetime.fromisoformat(updated)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        if dt >= cutoff:
                            recent_captures += 1
                except (ValueError, TypeError):
                    pass

        metrics = {
            "entries": total_entries,
            "recent_captures": recent_captures,
            "commands": 0,  # Placeholder — command tracking not yet implemented
        }
        return {"status": "ok", "metrics": metrics}

    except Exception:
        logger.exception("Failed to compute guide status metrics")
        return {
            "status": "error",
            "message": "Failed to compute metrics.",
        }


@router.post("/guide/park")
async def guide_park(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Save a stray thought to the library without context switching."""
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'text' in request payload.",
        )

    try:
        command_text = f"thought: {text}"
        handle_library_command(text=command_text, intent="library_thought")
        return {"status": "ok", "message": "Thought parked."}
    except Exception:
        logger.warning("Failed to park thought", exc_info=True)
        return {
            "status": "error",
            "message": "Failed to save thought to library.",
        }
