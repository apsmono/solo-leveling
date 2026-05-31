"""
Profile REST endpoints.

Provides GET/POST /profile for first-run detection and profile persistence.
All endpoints require Firebase authentication.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import require_auth
from src.core.profile_store import load_profile, save_profile

router = APIRouter()


@router.get("/profile")
async def get_profile(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Return 404 if no profile exists (first-run detection), else 200 + profile."""
    profile = load_profile()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile found. Complete onboarding first.",
        )
    return {"status": "ok", "profile": profile}


@router.post("/profile")
async def create_profile(
    payload: dict[str, Any],
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Save profile JSON and return it."""
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing profile data.",
        )
    save_profile(payload)
    return {"status": "ok", "profile": payload}
