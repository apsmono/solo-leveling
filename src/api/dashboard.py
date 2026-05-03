"""Dashboard data endpoints."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends

from src.api.deps import require_auth
from src.core.libraries import format_library_maintenance_summary

router = APIRouter()


@router.get("/dashboard/stats")
async def dashboard_stats(_: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    from src.core.libraries import _count_entries

    return {
        "library": {
            "profile": _count_entries("profile"),
            "terms": _count_entries("term"),
            "books": _count_entries("book"),
            "articles": _count_entries("article"),
            "thoughts": _count_entries("thought"),
            "references": _count_entries("reference"),
        },
        "integrations": _integration_health(),
    }


@router.get("/dashboard/health")
async def dashboard_health(_: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    return {"integrations": _integration_health()}


def _integration_health() -> dict[str, bool]:
    gmail_token_path = os.environ.get("GMAIL_TOKEN_PATH", ".gmail_token.json")
    gmail_ready = any(
        [
            os.environ.get("GMAIL_CREDENTIALS_PATH"),
            os.environ.get("GOOGLE_CREDENTIALS_PATH"),
            Path(gmail_token_path).exists(),
        ]
    )
    drive_ready = any(
        [
            os.environ.get("GOOGLE_DRIVE_CREDENTIALS_PATH"),
            os.environ.get("GOOGLE_CREDENTIALS_PATH"),
        ]
    )
    firebase_ready = any(
        [
            os.environ.get("FIREBASE_CREDENTIALS_PATH"),
            os.environ.get("FIREBASE_CREDENTIALS_JSON"),
        ]
    )
    return {
        "notion": bool(os.environ.get("NOTION_API_TOKEN")),
        "drive": drive_ready,
        "gmail": gmail_ready,
        "gemini": bool(os.environ.get("GEMINI_API_KEY")),
        "firebase": firebase_ready,
    }
