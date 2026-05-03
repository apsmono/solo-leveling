"""Command history REST endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from src.api.deps import require_auth
from src.core.config import USE_FIRESTORE_REMINDERS

router = APIRouter()


@router.get("/commands")
async def list_commands(
    limit: int = 50,
    _: dict[str, Any] = Depends(require_auth),
) -> list[dict[str, Any]]:
    if not USE_FIRESTORE_REMINDERS:
        return []
    from src.integrations.firebase.firestore import list_recent_commands
    return list_recent_commands(limit=limit)
