"""
Primary API server for the command center.

Exposes a generic command endpoint that routes plain text commands through
`src.core.router` without requiring a messaging adapter.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI

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


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/command")
async def command(payload: dict[str, Any]) -> dict[str, str]:
    text = str(payload.get("text", "")).strip()
    if not text:
        return {"status": "error", "reply": "Missing 'text' in request payload."}

    reply = route_command(text)
    return {"status": "ok", "reply": reply}
