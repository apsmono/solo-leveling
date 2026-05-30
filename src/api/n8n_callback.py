"""
n8n execution callback endpoint (N8N-04).

n8n workflows POST their execution results to this endpoint. Results are
persisted locally (local-first) with a rolling cap. The endpoint is
intentionally unauthenticated: n8n sends callbacks from the Docker internal
network, not the owner. A shared-secret header can be added later for
production hardening (cf. the Telegram webhook secret pattern).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter()

_EXECUTION_LOG_PATH = Path("data/n8n_executions.json")
_MAX_LOG_ENTRIES = 500


@router.post("/webhook/n8n")
async def n8n_callback(request: Request) -> dict[str, Any]:
    """Receive an n8n execution callback and persist it locally."""
    try:
        payload = await request.json()
    except Exception:  # noqa: BLE001 — malformed body must not 500
        return {"status": "error", "detail": "Invalid JSON"}

    if not isinstance(payload, dict):
        return {"status": "error", "detail": "Invalid JSON"}

    execution_id = payload.get("executionId") or payload.get("execution_id")
    status = payload.get("status", "")
    data = payload.get("data", {})
    logger.info("n8n callback: execution=%s status=%s", execution_id, status)
    _log_execution(str(execution_id) if execution_id is not None else "", status, data)
    return {"status": "ok"}


def _log_execution(execution_id: str, status: str, data: dict[str, Any]) -> None:
    """Append an execution record to the local store with a rolling cap."""
    entries: list[dict[str, Any]] = []
    if _EXECUTION_LOG_PATH.exists():
        try:
            entries = json.loads(_EXECUTION_LOG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            entries = []
    entries.append(
        {
            "execution_id": execution_id,
            "status": status,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    _EXECUTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _EXECUTION_LOG_PATH.write_text(
        json.dumps(entries[-_MAX_LOG_ENTRIES:], indent=2), encoding="utf-8"
    )
