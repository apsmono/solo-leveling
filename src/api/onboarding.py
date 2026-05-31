"""
Onboarding REST endpoints.

Provides POST /onboarding/parse-identity (LLM profile parsing) and
POST /profile/onboarding-step (step progress tracking).
All endpoints require Firebase authentication.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import require_auth
from src.core.onboarding import parse_identity
from src.core.profile_store import save_onboarding_step

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/onboarding/parse-identity")
async def parse_identity_endpoint(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Parse free text into a structured profile via LLM."""
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'text' in request payload.",
        )

    try:
        parsed = parse_identity(text)
        return {"status": "ok", "profile": parsed}
    except Exception:
        logger.exception("Failed to parse identity")
        return {
            "status": "error",
            "message": "Failed to parse identity. Please try again.",
        }


@router.post("/profile/onboarding-step")
async def onboarding_step_endpoint(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Save the current onboarding step (1-3)."""
    step = payload.get("step")
    if not isinstance(step, int) or step < 1 or step > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Step must be an integer between 1 and 3.",
        )

    save_onboarding_step(step)
    return {"status": "ok"}
