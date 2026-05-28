"""
Primary API server for the command center.

Exposes a generic command endpoint that routes plain text commands through
`src.core.router` without requiring a messaging adapter.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.deps import optional_auth
from src.core.config import FRONTEND_ORIGIN
from src.core.router import route_command
from src.core.scheduler import shutdown_scheduler, start_scheduler

logger = logging.getLogger(__name__)


def _startup_checks() -> None:
    """Ensure required runtime directories exist."""
    required_dirs = ["library", "data"]
    for name in required_dirs:
        path = Path(name)
        path.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    _startup_checks()
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(lifespan=lifespan)

# CORS for GitHub Pages frontend
_origins = ["http://localhost:8080", "http://localhost:3000"]
if FRONTEND_ORIGIN:
    _origins.append(FRONTEND_ORIGIN)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Versioned API routers
from src.api.v1_router import router as v1_router

app.include_router(v1_router)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/command")
async def command(
    payload: dict[str, Any],
    user: Optional[dict[str, Any]] = Depends(optional_auth),
) -> dict[str, str]:
    text = str(payload.get("text", "")).strip()
    if not text:
        return {"status": "error", "reply": "Missing 'text' in request payload."}

    source = f"api:{user['email']}" if user else "api"
    reply = route_command(text, source=source)
    return {"status": "ok", "reply": reply}


@app.post("/webhook/telegram")
async def telegram_webhook(payload: dict[str, Any]) -> dict[str, str]:
    """Receive Telegram webhook updates."""
    from src.core.config import TELEGRAM_WEBHOOK_SECRET
    from src.integrations.telegram.webhook import process_update

    secret = payload.get("secret", "")
    if TELEGRAM_WEBHOOK_SECRET and secret != TELEGRAM_WEBHOOK_SECRET:
        logger.warning("Telegram webhook received with invalid secret.")
        return {"status": "ok"}

    try:
        await process_update(payload)
    except Exception:
        logger.exception("Telegram webhook error")
    return {"status": "ok"}
