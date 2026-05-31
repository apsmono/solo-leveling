"""
Onboarding REST endpoints.

Provides:
  - POST /onboarding/parse-identity  — LLM profile parsing
  - POST /profile/onboarding-step    — step progress tracking
  - POST /onboarding/connect-app     — record an app connection in the profile
  - GET  /onboarding/digest          — generate a 3-bullet 24-hour digest

All endpoints require Firebase authentication.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import require_auth
from src.core.onboarding import generate_digest, parse_identity, _query_connected_sources
from src.core.profile_store import load_profile, save_onboarding_step, save_profile

logger = logging.getLogger(__name__)

router = APIRouter()

_ALLOWED_APPS = frozenset({"gmail", "youtube", "notion", "gdrive", "github", "telegram", "discord"})


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
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to parse identity. Please try again.",
        ) from None


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


@router.post("/onboarding/connect-app")
async def connect_app_endpoint(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Record an app connection in the owner's profile.

    Validates the app name against the allowed list (T-05-05 mitigation) and
    appends it to profile['connected_apps']. Actual OAuth flows are handled by
    the brain's integration layer; this endpoint only records the connection.
    """
    app = payload.get("app", "")
    if not isinstance(app, str) or not app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'app' in request payload.",
        )

    app = app.strip().lower()
    if app not in _ALLOWED_APPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown app '{app}'. Allowed: {sorted(_ALLOWED_APPS)}.",
        )

    profile = load_profile() or {}
    connected: list[str] = profile.get("connected_apps", [])
    if app not in connected:
        connected.append(app)
    profile["connected_apps"] = connected
    save_profile(profile)

    logger.info("App connected: %s", app)
    return {"status": "ok", "message": f"{app} connected"}


@router.get("/onboarding/digest")
async def digest_endpoint(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Generate a 3-bullet 24-hour digest from connected sources.

    On cold start (no connected apps or all fetches fail), returns a capability
    preview instead of empty content (D-13).
    """
    profile = load_profile() or {}
    connected_data = _query_connected_sources(profile)
    bullets = generate_digest(profile, connected_data)
    return {"status": "ok", "bullets": bullets[:3]}
