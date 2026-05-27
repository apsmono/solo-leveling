"""Timeline / chronological stream REST endpoints."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query

from src.api.deps import require_auth

router = APIRouter()

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LIBRARY_ROOT = _PROJECT_ROOT / "library"
_INDEX_PATH = _LIBRARY_ROOT / "index.json"


def _load_index() -> dict[str, Any]:
    if _INDEX_PATH.exists():
        return json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
    return {"entries": [], "bundles": []}


def _extract_captured_at(text: str) -> Optional[str]:
    cap_match = re.search(r"^captured_at:\s*(.+)$", text, flags=re.MULTILINE)
    return cap_match.group(1).strip() if cap_match else None


@router.get("/library/timeline")
async def get_timeline(
    section: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    index = _load_index()
    entries = index.get("entries", [])

    events: list[dict[str, Any]] = []
    for e in entries:
        path = _PROJECT_ROOT / e.get("path", "")
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        captured_at = _extract_captured_at(text) or e.get("updated_at", "")

        if not captured_at:
            continue

        # Normalize date
        try:
            dt = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
        except Exception:
            continue

        if section and section.lower() not in str(e.get("section", "")).lower():
            continue
        if from_date and date_str < from_date:
            continue
        if to_date and date_str > to_date:
            continue

        events.append({
            "id": Path(e.get("path", "")).stem,
            "title": e.get("title", ""),
            "section": e.get("section", ""),
            "status": e.get("status", ""),
            "date": date_str,
            "datetime": captured_at,
        })

    # Group by date
    events.sort(key=lambda x: x["date"], reverse=True)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ev in events:
        grouped[ev["date"]].append(ev)

    days = [
        {"date": date, "entries": grouped[date]}
        for date in sorted(grouped.keys(), reverse=True)
    ]

    # Activity stats
    daily_counts: dict[str, int] = {}
    for d in days:
        daily_counts[d["date"]] = len(d["entries"])

    return {
        "days": days,
        "total": len(events),
        "daily_counts": daily_counts,
    }
