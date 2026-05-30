"""Library browsing REST endpoints."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import require_auth
from src.agents.dispatcher import run_agent
from src.core.libraries import _get_store
from src.core.library_store import SORT_FIELD_MAP
from src.integrations.youtube import extract_video_id, fetch_transcript
from src.vector.search import search_library

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
    return _get_store().build_index()


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
    entry_tags = set(entry.get("tags", []))
    if not entry_tags:
        entry_tags = {entry.get("section", ""), entry.get("category", "")}

    related: list[tuple[str, int]] = []
    for other in all_entries:
        if other.get("path") == entry.get("path"):
            continue
        other_tags = set(other.get("tags", []))
        if not other_tags:
            other_tags = {other.get("section", ""), other.get("category", "")}

        shared = len(entry_tags & other_tags)
        if shared > 0:
            related.append((_entry_id_from_path(other.get("path", "")), shared))

    related.sort(key=lambda x: x[1], reverse=True)
    return [rid for rid, _ in related[:5]]


def _enrich_entry(record: dict[str, Any]) -> dict[str, Any]:
    """Add derived fields (id, tags, captured_at, source_url) to a store record."""
    path = record.get("path", "")
    entry_id = _entry_id_from_path(path) if path else record.get("entry_id", "")

    # Tags may come from Firestore; fallback to filesystem extraction
    tags = record.get("tags", [])
    captured_at = record.get("captured_at", "")
    source_url = record.get("source_url")

    if not tags and path:
        entry_path = _PROJECT_ROOT / path
        if entry_path.exists():
            text = entry_path.read_text(encoding="utf-8", errors="ignore")
            tags = _extract_tags(text)
            if not captured_at:
                captured_at = _extract_captured_at(text)
            if source_url is None:
                source_url = _extract_source_url(text)

    return {
        "id": entry_id,
        "title": record.get("title", ""),
        "section": record.get("section", ""),
        "category": record.get("category", ""),
        "status": record.get("status", ""),
        "type": record.get("type", ""),
        "tags": tags if isinstance(tags, list) else [],
        "captured_at": captured_at,
        "source_url": source_url,
        "path": path,
    }


def _resolve_sort_param(sort: Optional[str], order: Optional[str]) -> tuple[str, bool]:
    """Resolve sort param to (field_name, reverse) tuple. Duplicates store logic for search path."""
    if sort and sort in SORT_FIELD_MAP:
        return SORT_FIELD_MAP[sort]
    if sort in ("captured_at", "updated_at", "title", "section", "status", "type"):
        reverse = (order or "desc").lower() == "desc"
        return sort, reverse
    return "captured_at", True  # default: newest first


@router.get("/library/entries")
async def list_entries(
    section: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    source_url: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    store = _get_store()

    if search:
        # Use store search for text queries, then paginate
        results = store.search_entries(search, section=section, limit=per_page * page)
        # Apply client-side filters
        if status:
            results = [r for r in results if status.lower() in str(r.get("status", "")).lower()]
        if tag:
            results = [r for r in results if tag.lower() in [t.lower() for t in r.get("tags", [])]]
        if source_url:
            results = [r for r in results if r.get("source_url") == source_url]

        # Sort before paginating in search path
        sort_field, reverse = _resolve_sort_param(sort, order)
        def _sort_key(entry: dict[str, Any]) -> str:
            val = entry.get(sort_field, "")
            return str(val) if val is not None else ""
        results.sort(key=_sort_key, reverse=reverse)

        total = len(results)
        start = (page - 1) * per_page
        page_results = results[start:start + per_page]
    else:
        # Use store list for paginated queries
        result = store.list_entries(
            section=section,
            status=status,
            tag=tag,
            source_url=source_url,
            page=page,
            per_page=per_page,
            sort=sort,
            order=order,
        )
        total = result["total"]
        page_results = result["entries"]

    # Enrich each record with derived fields
    entries = [_enrich_entry(e) for e in page_results]

    return {
        "entries": entries,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/library/entries/{entry_id}")
async def get_entry(
    entry_id: str,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    store = _get_store()
    data = store.get_entry(entry_id)

    if not data:
        raise HTTPException(status_code=404, detail="Entry not found.")

    # Build related entries from the full index
    index = _load_index()
    all_entries = index.get("entries", [])

    return {
        "id": entry_id,
        "title": data.get("title", ""),
        "section": data.get("section", ""),
        "category": data.get("category", ""),
        "status": data.get("status", ""),
        "type": data.get("type", ""),
        "tags": data.get("tags", []) if isinstance(data.get("tags"), list) else [],
        "captured_at": data.get("captured_at", ""),
        "source_url": data.get("source_url"),
        "path": data.get("path", ""),
        "markdown": data.get("markdown", ""),
        "related": _compute_related(data, all_entries),
    }


@router.delete("/library/entries/{entry_id}")
async def delete_entry_endpoint(
    entry_id: str,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Delete a library entry by ID."""
    store = _get_store()
    deleted = store.delete_entry(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Entry not found: {entry_id}")
    return {"status": "ok", "id": entry_id}


@router.get("/library/sections")
async def list_sections(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    return {"sections": _get_store().list_sections()}


@router.get("/library/tags")
async def list_tags(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    return {"tags": _get_store().list_tags()}


@router.post("/library/youtube-transcript")
async def youtube_transcript(
    payload: dict[str, Any],
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Fetch YouTube transcript for a given URL."""
    url = str(payload.get("url", "")).strip()
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in request body.")

    video_id = extract_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Could not extract video ID from URL.")

    transcript = fetch_transcript(video_id)
    if transcript is None:
        raise HTTPException(status_code=404, detail="Transcript unavailable for this video.")

    return {
        "video_id": video_id,
        "title": "",  # Caller already has title from preview
        "transcript": transcript,
        "language": "auto",
        "is_generated": True,
    }


@router.put("/library/entries/{entry_id}")
async def update_entry(
    entry_id: str,
    payload: dict[str, Any],
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Update a library entry's frontmatter and body."""
    store = _get_store()
    data = store.get_entry(entry_id)

    if not data:
        raise HTTPException(status_code=404, detail="Entry not found.")

    path = data.get("path", "")
    entry_path = _PROJECT_ROOT / path
    if not entry_path.exists():
        raise HTTPException(status_code=404, detail="Entry file not found.")

    text = entry_path.read_text(encoding="utf-8", errors="ignore")

    # Extract existing frontmatter
    title_match = re.search(r"^title:\s*(.+)$", text, flags=re.MULTILINE)
    section_match = re.search(r"^section:\s*(.+)$", text, flags=re.MULTILINE)
    status_match = re.search(r"^status:\s*(.+)$", text, flags=re.MULTILINE)
    captured_at_match = re.search(r"^captured_at:\s*(.+)$", text, flags=re.MULTILINE)
    source_url_match = re.search(r"^source_url:\s*(.+)$", text, flags=re.MULTILINE)

    # Build updated values
    new_title = payload.get("title", title_match.group(1).strip() if title_match else data.get("title", ""))
    new_status = payload.get("status", status_match.group(1).strip() if status_match else data.get("status", "draft"))
    new_tags = payload.get("tags", _extract_tags(text))
    new_markdown = payload.get("markdown", "")
    new_notes = payload.get("notes", "")

    section = section_match.group(1).strip() if section_match else data.get("section", "")
    captured_at = captured_at_match.group(1).strip() if captured_at_match else ""
    source_url = source_url_match.group(1).strip() if source_url_match else ""

    metadata_tags = ", ".join(new_tags) if isinstance(new_tags, list) else str(new_tags)
    source_url_line = f"source_url: {source_url}\n" if source_url else ""

    # Determine body
    if new_markdown:
        body = new_markdown
    else:
        parts = text.split("---\n", 2)
        body = parts[2].strip() if len(parts) >= 3 else text

    # Append notes if provided
    if new_notes:
        body += f"\n\n## My Notes\n\n{new_notes}\n"

    content = (
        f"---\n"
        f"title: {new_title}\n"
        f"section: {section}\n"
        f"status: {new_status}\n"
        f"tags: [{metadata_tags}]\n"
        f"captured_at: {captured_at}\n"
        f"{source_url_line}"
        f"---\n\n"
        f"{body}\n"
    )
    entry_path.write_text(content, encoding="utf-8")

    # Rebuild index so subsequent reads reflect the change
    from src.core.libraries import _build_library_index
    _build_library_index()

    # Best-effort Firestore update with full content
    try:
        store.update_entry(
            entry_id,
            {
                "title": new_title,
                "status": new_status,
                "tags": new_tags,
                "markdown": content,
            },
        )
    except Exception:
        import logging
        logging.getLogger(__name__).warning("Firestore update failed", exc_info=True)

    return {"status": "ok", "id": entry_id}


@router.post("/library/search")
async def search_library_endpoint(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Search library entries by keyword, vector, or hybrid mode."""
    query = str(payload.get("query", "")).strip()
    if not query:
        raise HTTPException(status_code=400, detail="Missing 'query' in request body.")

    mode = str(payload.get("mode", "hybrid")).strip().lower()
    if mode not in ("keyword", "vector", "hybrid"):
        raise HTTPException(status_code=400, detail="Invalid mode. Use: keyword, vector, or hybrid.")

    limit = int(payload.get("limit", 12))
    if limit < 1:
        limit = 1
    elif limit > 50:
        limit = 50

    owner_id = user.get("email", user.get("uid", "default-owner"))

    results = await search_library(query, owner_id, mode=mode, limit=limit)
    entries = [_enrich_entry(e) for e in results]

    return {
        "entries": entries,
        "total": len(entries),
        "mode": mode,
        "query": query,
    }


@router.get("/library/recent")
async def list_recent_entries(
    limit: int = Query(4, ge=1, le=10),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Return the N most recent library entries sorted by updated_at."""
    index = _load_index()
    all_entries = index.get("entries", [])

    # Sort by updated_at descending, fallback to captured_at if updated_at missing
    def _sort_key(entry: dict[str, Any]) -> str:
        return str(entry.get("updated_at", entry.get("captured_at", "")))

    sorted_entries = sorted(
        all_entries,
        key=_sort_key,
        reverse=True,
    )

    recent = sorted_entries[:limit]
    entries = [_enrich_entry(e) for e in recent]

    return {
        "entries": entries,
        "total": len(entries),
    }


@router.post("/library/entries/{entry_id}/synthesize")
async def synthesize_entry(
    entry_id: str,
    payload: dict[str, Any],
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ask AI a question about a specific library entry."""
    query = str(payload.get("query", "")).strip()
    if not query:
        return {"status": "error", "reply": "Missing 'query' in request body."}

    store = _get_store()
    data = store.get_entry(entry_id)

    if not data:
        raise HTTPException(status_code=404, detail="Entry not found.")

    text = data.get("markdown", "")

    # Auto-enrich YouTube entries with transcript if the file is a metadata stub
    source_url = data.get("source_url", "")
    if source_url and extract_video_id(source_url):
        body_start = text.find("\n\n")
        body = text[body_start + 2 :] if body_start > 0 else ""
        body_stripped = body.strip()
        # If the body is empty or looks like a placeholder stub, fetch transcript
        if not body_stripped or len(body_stripped) < 200:
            video_id = extract_video_id(source_url)
            if video_id:
                transcript = fetch_transcript(video_id)
                if transcript:
                    text = f"{text.rstrip()}\n\n## Transcript\n\n{transcript}\n"

    # Truncate to avoid token limits
    truncated = text[:4000] + ("\n... [truncated]" if len(text) > 4000 else "")

    task = (
        f"User question about the following document:\n{query}\n\n"
        f"Document title: {data.get('title', '')}\n"
        f"Document content:\n{truncated}\n\n"
        f"Answer the question based ONLY on the provided document. "
        f"If the document does not contain the answer, say so clearly."
    )

    try:
        answer = run_agent(task=task)
    except Exception as e:
        return {"status": "error", "reply": f"AI synthesis failed: {e}"}

    return {
        "status": "ok",
        "answer": answer,
        "sources": [data.get("title", entry_id)],
    }
