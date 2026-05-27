"""Knowledge graph REST endpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends

from src.api.deps import require_auth

router = APIRouter()

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LIBRARY_ROOT = _PROJECT_ROOT / "library"
_INDEX_PATH = _LIBRARY_ROOT / "index.json"

_SECTION_COLORS = {
    "profile": "#38bdf8",
    "term": "#a78bfa",
    "book": "#fbbf24",
    "article": "#34d399",
    "thought": "#f472b6",
    "reference": "#94a3b8",
    "research": "#fb923c",
}


def _load_index() -> dict[str, Any]:
    if _INDEX_PATH.exists():
        return json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
    return {"entries": [], "bundles": []}


def _extract_tags(text: str) -> list[str]:
    import re
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


@router.get("/library/graph")
async def get_graph(
    max_nodes: int = 200,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    index = _load_index()
    entries = index.get("entries", [])[:max_nodes]

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    entry_tags: dict[str, set[str]] = {}
    entry_sections: dict[str, str] = {}

    for e in entries:
        entry_id = Path(e.get("path", "")).stem
        section = e.get("section", "unknown")
        entry_sections[entry_id] = section

        path = _PROJECT_ROOT / e.get("path", "")
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        tags = _extract_tags(text)
        entry_tags[entry_id] = set(t.lower() for t in tags)

        nodes.append({
            "id": entry_id,
            "label": e.get("title", entry_id),
            "section": section,
            "status": e.get("status", "unknown"),
            "color": _SECTION_COLORS.get(section, "#94a3b8"),
            "size": max(5, min(20, 5 + len(tags) * 2)),
        })

    # Build edges from shared tags
    entry_ids = list(entry_tags.keys())
    for i in range(len(entry_ids)):
        for j in range(i + 1, len(entry_ids)):
            id_a = entry_ids[i]
            id_b = entry_ids[j]
            shared = entry_tags[id_a] & entry_tags[id_b]
            if shared:
                edges.append({
                    "source": id_a,
                    "target": id_b,
                    "type": "shared_tag",
                    "tags": list(shared),
                    "weight": len(shared),
                })
            elif entry_sections.get(id_a) == entry_sections.get(id_b):
                # Weak same-section edge
                edges.append({
                    "source": id_a,
                    "target": id_b,
                    "type": "same_section",
                    "section": entry_sections[id_a],
                    "weight": 1,
                })

    return {"nodes": nodes, "edges": edges}
