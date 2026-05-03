"""Firebase Admin SDK initialization and ID token verification."""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import HTTPException, status

from src.core.config import (
    ALLOWED_USER_EMAIL,
    FIREBASE_CREDENTIALS_JSON,
    FIREBASE_CREDENTIALS_PATH,
)

logger = logging.getLogger(__name__)

_FIREBASE_APP: Any | None = None


def _init_firebase() -> None:
    global _FIREBASE_APP
    if _FIREBASE_APP is not None:
        return
    try:
        import firebase_admin
        from firebase_admin import credentials
    except ModuleNotFoundError as exc:
        raise EnvironmentError("firebase-admin is not installed.") from exc

    if FIREBASE_CREDENTIALS_JSON:
        cred = credentials.Certificate.from_json(FIREBASE_CREDENTIALS_JSON)
    elif FIREBASE_CREDENTIALS_PATH:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    else:
        raise EnvironmentError(
            "Firebase credentials not configured. Set FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_PATH."
        )
    _FIREBASE_APP = firebase_admin.initialize_app(cred)


def verify_id_token(token: str) -> dict[str, Any]:
    _init_firebase()
    from firebase_admin import auth

    try:
        decoded = auth.verify_id_token(token, clock_skew_seconds=10)
    except Exception as exc:
        logger.warning("Firebase ID token verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        ) from exc

    if ALLOWED_USER_EMAIL:
        email = decoded.get("email", "")
        if email.lower() != ALLOWED_USER_EMAIL.lower():
            logger.warning("Unauthorized user email: %s", email)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not authorized.",
            )

    return decoded
