"""Analysis REST endpoints — tags, gaps, trends, AI synthesis."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends

from src.api.deps import require_auth
from src.agents.dispatcher import run_agent

router = APIRouter()

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LIBRARY_ROOT = _PROJECT_ROOT / "library"
_INDEX_PATH = _LIBRARY_ROOT / "index.json"


def _load_index() -> dict[str, Any]:
    if _INDEX_PATH.exists():
        return json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
    return {"entries": [], "bundles": []}


def _extract_tags(text: str) -> list[str]:
    tags_match = re.search(r"^tags:\s*(.+)$", text, flags=re.MULTILINE)
    if not tags_match:
        return []
    raw = tags_match.group(1).strip()
    if raw.startswith("["):
        try:
            return json.loads(raw.replace("'", '"'))
        except Exception:
            pass
    return [t.strip() for t in raw.strip("[]").split(",") if t.strip()]


def _extract_captured_at(text: str) -> Optional[datetime]:
    cap_match = re.search(r"^captured_at:\s*(.+)$", text, flags=re.MULTILINE)
    if cap_match:
        try:
            return datetime.fromisoformat(cap_match.group(1).strip().replace("Z", "+00:00"))
        except Exception:
            pass
    return None


@router.get("/analysis/tags")
async def get_tags(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    index = _load_index()
    entries = index.get("entries", [])

    all_tags: list[str] = []
    co_occurrence: dict[tuple[str, str], int] = defaultdict(int)

    for e in entries:
        path = _PROJECT_ROOT / e.get("path", "")
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        tags = [t.lower() for t in _extract_tags(text)]
        all_tags.extend(tags)

        # Co-occurrence
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                a, b = sorted([tags[i], tags[j]])
                co_occurrence[(a, b)] += 1

    frequencies = Counter(all_tags)
    total_entries = len(entries)

    # Trending = tags that appear in entries from last 30 days
    now = datetime.now()
    recent_tags: list[str] = []
    for e in entries:
        path = _PROJECT_ROOT / e.get("path", "")
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        cap = _extract_captured_at(text)
        if cap and (now - cap) <= timedelta(days=30):
            recent_tags.extend(t.lower() for t in _extract_tags(text))

    trending = [tag for tag, _ in Counter(recent_tags).most_common(10)]

    # Orphan tags = appear only once
    orphan_tags = [tag for tag, count in frequencies.items() if count == 1]

    # Co-occurrence pairs
    co_list = [
        [a, b, count]
        for (a, b), count in sorted(co_occurrence.items(), key=lambda x: x[1], reverse=True)
    ][:20]

    return {
        "frequencies": dict(frequencies.most_common()),
        "trending": trending,
        "orphan_tags": orphan_tags,
        "co_occurrence": co_list,
    }


@router.get("/analysis/gaps")
async def get_gaps(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    index = _load_index()
    entries = index.get("entries", [])

    section_counts: dict[str, int] = defaultdict(int)
    stale_entries: list[dict[str, Any]] = []
    orphan_entries: list[dict[str, Any]] = []
    now = datetime.now()

    for e in entries:
        section = e.get("section", "unknown")
        section_counts[section] += 1

        path = _PROJECT_ROOT / e.get("path", "")
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        tags = _extract_tags(text)
        cap = _extract_captured_at(text)

        entry_id = Path(e.get("path", "")).stem

        # Stale = no update in 90 days
        if cap and (now - cap) > timedelta(days=90):
            stale_entries.append({
                "id": entry_id,
                "title": e.get("title", ""),
                "section": section,
                "days_since_update": (now - cap).days,
            })

        # Orphan = no tags
        if not tags:
            orphan_entries.append({
                "id": entry_id,
                "title": e.get("title", ""),
                "section": section,
            })

    # Empty sections = sections with < 2 entries
    all_sections = {"profile", "term", "book", "article", "thought", "reference", "research"}
    empty_sections = [s for s in all_sections if section_counts.get(s, 0) < 2]

    return {
        "empty_sections": empty_sections,
        "stale_entries": stale_entries[:20],
        "orphan_entries": orphan_entries[:20],
        "section_counts": dict(section_counts),
    }


@router.post("/analysis/synthesize")
async def synthesize(
    payload: dict[str, Any],
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    query = str(payload.get("query", "")).strip()
    entry_ids = payload.get("entry_ids", [])

    if not query:
        return {"status": "error", "reply": "Missing 'query' in request."}

    index = _load_index()
    entries = index.get("entries", [])

    # Collect markdown texts
    texts: list[str] = []
    sources: list[str] = []

    for e in entries:
        entry_id = Path(e.get("path", "")).stem
        if entry_ids and entry_id not in entry_ids:
            continue
        if entry_ids and entry_id in entry_ids:
            path = _PROJECT_ROOT / e.get("path", "")
            text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
            # Truncate to avoid token limits
            truncated = text[:2000] + ("\n... [truncated]" if len(text) > 2000 else "")
            texts.append(f"--- {e.get('title', entry_id)} ---\n{truncated}")
            sources.append(e.get("title", entry_id))

    if not texts:
        return {"status": "error", "reply": "No matching entries found."}

    context = "\n\n".join(texts[:5])  # Limit to 5 entries for token budget
    task = (
        f"User question: {query}\n\n"
        f"Here are relevant library entries:\n\n{context}\n\n"
        f"Synthesize a concise answer based ONLY on the provided entries. "
        f"Cite which entries you used. If the entries don't answer the question, say so."
    )

    try:
        synthesis = run_agent(task=task)
    except Exception as e:
        return {"status": "error", "reply": f"AI synthesis failed: {e}"}

    return {
        "status": "ok",
        "synthesis": synthesis,
        "sources": sources[:5],
    }


@router.get("/analysis/activity")
async def get_activity(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    index = _load_index()
    entries = index.get("entries", [])

    daily_counts: dict[str, int] = defaultdict(int)
    section_growth: dict[str, int] = defaultdict(int)
    now = datetime.now()
    earliest: Optional[datetime] = None

    for e in entries:
        section = e.get("section", "unknown")
        section_growth[section] += 1

        path = _PROJECT_ROOT / e.get("path", "")
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        cap = _extract_captured_at(text)
        if cap:
            daily_counts[cap.strftime("%Y-%m-%d")] += 1
            if earliest is None or cap < earliest:
                earliest = cap

    total_days = max(1, (now - earliest).days) if earliest else 1
    velocity = round(len(entries) * 7 / total_days, 1) if total_days > 0 else 0

    return {
        "daily_counts": dict(daily_counts),
        "section_growth": dict(section_growth),
        "capture_velocity": f"{velocity} entries/week",
        "total_entries": len(entries),
    }
