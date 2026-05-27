"""Library browsing REST endpoints."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import require_auth

router = APIRouter()

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LIBRARY_ROOT = _PROJECT_ROOT / "library"
_INDEX_PATH = _LIBRARY_ROOT / "index.json"

_SECTION_DIRS = {
    "profile": "profile",
    "term": "terms",
    "book": "books",
    "article": "articles",
    "thought": "thoughts",
    "reference": "references",
    "research": "research",
}


def _load_index() -> dict[str, Any]:
    if _INDEX_PATH.exists():
        return json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
    return {"entries": [], "bundles": []}


def _entry_id_from_path(path: str) -> str:
    """Derive a stable entry ID from its relative path."""
    p = Path(path)
    if p.name == "index.md":
        return p.parent.name
    return p.stem


def _extract_tags(text: str) -> list[str]:
    tags_match = re.search(r"^tags:\s*(.+)$", text, flags=re.MULTILINE)
    if not tags_match:
        return []
    raw = tags_match.group(1).strip()
    # Handle YAML list syntax: ["a", "b"] or a, b
    if raw.startswith("["):
        try:
            return json.loads(raw.replace("'", '"'))
        except Exception:
            pass
    return [t.strip() for t in raw.strip("[]").split(",") if t.strip()]


def _extract_captured_at(text: str) -> str:
    cap_match = re.search(r"^captured_at:\s*(.+)$", text, flags=re.MULTILINE)
    return cap_match.group(1).strip() if cap_match else ""


def _extract_source_url(text: str) -> Optional[str]:
    url_match = re.search(r"^source_url:\s*(.+)$", text, flags=re.MULTILINE)
    return url_match.group(1).strip() if url_match else None


def _compute_related(entry: dict[str, Any], all_entries: list[dict[str, Any]]) -> list[str]:
    """Find related entries by shared tags or section."""
    path = entry.get("path", "")
    entry_text = ""
    entry_path = _PROJECT_ROOT / path
    if entry_path.exists():
        entry_text = entry_path.read_text(encoding="utf-8", errors="ignore")
    entry_tags = set(_extract_tags(entry_text))
    if not entry_tags:
        entry_tags = {entry.get("section", ""), entry.get("category", "")}

    related: list[tuple[str, int]] = []
    for other in all_entries:
        if other.get("path") == path:
            continue
        other_text = ""
        other_path = _PROJECT_ROOT / other.get("path", "")
        if other_path.exists():
            other_text = other_path.read_text(encoding="utf-8", errors="ignore")
        other_tags = set(_extract_tags(other_text))
        if not other_tags:
            other_tags = {other.get("section", ""), other.get("category", "")}

        shared = len(entry_tags & other_tags)
        if shared > 0:
            related.append((_entry_id_from_path(other.get("path", "")), shared))

    related.sort(key=lambda x: x[1], reverse=True)
    return [rid for rid, _ in related[:5]]


@router.get("/library/entries")
async def list_entries(
    section: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    source_url: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    index = _load_index()
    entries = index.get("entries", [])

    # Filters
    if section:
        entries = [e for e in entries if section.lower() in str(e.get("section", "")).lower()]
    if status:
        entries = [e for e in entries if status.lower() in str(e.get("status", "")).lower()]
    if tag:
        entries = [
            e for e in entries
            if tag.lower() in [t.lower() for t in _extract_tags(
                (_PROJECT_ROOT / e.get("path", "")).read_text(encoding="utf-8", errors="ignore")
                if (_PROJECT_ROOT / e.get("path", "")).exists() else ""
            )]
        ]
    if source_url:
        entries = [e for e in entries if e.get("source_url") == source_url]
    if search:
        q = search.lower()
        entries = [
            e for e in entries
            if q in str(e.get("title", "")).lower()
            or q in str(e.get("section", "")).lower()
            or q in str(e.get("category", "")).lower()
            or q in str(e.get("source_url", "")).lower()
        ]

    total = len(entries)
    start = (page - 1) * per_page
    end = start + per_page
    page_entries = entries[start:end]

    # Enrich with id and tags
    results = []
    for e in page_entries:
        path = e.get("path", "")
        entry_path = _PROJECT_ROOT / path
        text = entry_path.read_text(encoding="utf-8", errors="ignore") if entry_path.exists() else ""
        results.append({
            "id": _entry_id_from_path(path),
            "title": e.get("title", ""),
            "section": e.get("section", ""),
            "category": e.get("category", ""),
            "status": e.get("status", ""),
            "type": e.get("type", ""),
            "tags": _extract_tags(text),
            "captured_at": _extract_captured_at(text),
            "source_url": _extract_source_url(text),
            "path": path,
        })

    return {
        "entries": results,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/library/entries/{entry_id}")
async def get_entry(
    entry_id: str,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    index = _load_index()
    all_entries = index.get("entries", [])

    # Find entry by id
    matched = None
    for e in all_entries:
        if _entry_id_from_path(e.get("path", "")) == entry_id:
            matched = e
            break

    if not matched:
        raise HTTPException(status_code=404, detail="Entry not found.")

    path = matched.get("path", "")
    entry_path = _PROJECT_ROOT / path
    if not entry_path.exists():
        raise HTTPException(status_code=404, detail="Entry file not found.")

    text = entry_path.read_text(encoding="utf-8", errors="ignore")

    return {
        "id": entry_id,
        "title": matched.get("title", ""),
        "section": matched.get("section", ""),
        "category": matched.get("category", ""),
        "status": matched.get("status", ""),
        "type": matched.get("type", ""),
        "tags": _extract_tags(text),
        "captured_at": _extract_captured_at(text),
        "source_url": _extract_source_url(text),
        "path": path,
        "markdown": text,
        "related": _compute_related(matched, all_entries),
    }


@router.get("/library/sections")
async def list_sections(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    return {"sections": list(_SECTION_DIRS.keys())}


@router.get("/library/tags")
async def list_tags(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    index = _load_index()
    entries = index.get("entries", [])
    all_tags: set[str] = set()
    for e in entries:
        path = _PROJECT_ROOT / e.get("path", "")
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="ignore")
            all_tags.update(_extract_tags(text))
    return {"tags": sorted(all_tags)}
