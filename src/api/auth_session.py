"""Firebase session cookie login/logout endpoints."""

from __future__ import annotations

import datetime
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Response, status

from src.core.config import SESSION_COOKIE_SECURE
from src.integrations.firebase.auth import _init_firebase, verify_id_token

logger = logging.getLogger(__name__)

router = APIRouter()
_SESSION_DURATION = datetime.timedelta(days=7)

# Module-level import so tests can patch fb_auth.create_session_cookie
import firebase_admin.auth as fb_auth


@router.post("/auth/session-login")
async def session_login(payload: dict[str, Any], response: Response) -> dict[str, str]:
    id_token = payload.get("idToken", "")
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing idToken."
        )

    try:
        verify_id_token(id_token)
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("ID token verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        ) from exc

    _init_firebase()

    try:
        cookie = fb_auth.create_session_cookie(id_token, expires_in=_SESSION_DURATION)
    except Exception as exc:
        logger.warning("Session cookie creation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        ) from exc

    response.set_cookie(
        key="__session",
        value=cookie,
        max_age=int(_SESSION_DURATION.total_seconds()),
        httponly=True,
        secure=SESSION_COOKIE_SECURE,
        samesite="strict",
    )
    return {"status": "ok"}


@router.post("/auth/session-logout")
async def session_logout(response: Response) -> dict[str, str]:
    response.delete_cookie("__session")
    return {"status": "ok"}
