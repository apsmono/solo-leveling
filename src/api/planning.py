"""Planning REST endpoints — goals, projects, reviews."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends

from src.api.deps import require_auth
from src.agents.dispatcher import run_agent

router = APIRouter()

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LIBRARY_ROOT = _PROJECT_ROOT / "library"
_INDEX_PATH = _LIBRARY_ROOT / "index.json"

_PLANNING_SECTIONS = {"goals", "projects", "reviews"}


def _load_index() -> dict[str, Any]:
    if _INDEX_PATH.exists():
        return json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
    return {"entries": [], "bundles": []}


def _extract_status(text: str) -> str:
    status_match = re.search(r"^status:\s*(.+)$", text, flags=re.MULTILINE)
    return status_match.group(1).strip() if status_match else "unknown"


def _extract_captured_at(text: str) -> Optional[datetime]:
    cap_match = re.search(r"^captured_at:\s*(.+)$", text, flags=re.MULTILINE)
    if cap_match:
        try:
            return datetime.fromisoformat(cap_match.group(1).strip().replace("Z", "+00:00"))
        except Exception:
            pass
    return None


def _read_planning_entries(kind: str) -> list[dict[str, Any]]:
    """Read entries from library/{kind}/ directory."""
    entries: list[dict[str, Any]] = []
    dir_path = _LIBRARY_ROOT / kind
    if not dir_path.exists():
        return entries

    for path in sorted(dir_path.rglob("*.md")):
        if path.name == ".gitkeep":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        title_match = re.search(r"^title:\s*(.+)$", text, flags=re.MULTILINE)
        title = title_match.group(1).strip() if title_match else path.stem
        status = _extract_status(text)
        cap = _extract_captured_at(text)

        entries.append({
            "id": path.stem,
            "title": title,
            "status": status,
            "path": str(path.relative_to(_PROJECT_ROOT)),
            "captured_at": cap.isoformat() if cap else None,
            "preview": text[:300] + ("..." if len(text) > 300 else ""),
        })

    return entries


@router.get("/planning/goals")
async def get_goals(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    goals = _read_planning_entries("goals")
    return {
        "goals": goals,
        "active": [g for g in goals if g.get("status") == "active"],
        "completed": [g for g in goals if g.get("status") == "completed"],
        "paused": [g for g in goals if g.get("status") not in ("active", "completed")],
    }


@router.get("/planning/projects")
async def get_projects(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    projects = _read_planning_entries("projects")
    return {
        "projects": projects,
        "active": [p for p in projects if p.get("status") == "active"],
        "completed": [p for p in projects if p.get("status") == "completed"],
    }


@router.get("/planning/reviews")
async def get_reviews(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    reviews = _read_planning_entries("reviews")
    return {"reviews": reviews}


@router.post("/planning/review")
async def generate_review(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Generate a weekly review from recent captures."""
    index = _load_index()
    entries = index.get("entries", [])
    now = datetime.now()

    recent: list[str] = []
    for e in entries:
        path = _PROJECT_ROOT / e.get("path", "")
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        cap = _extract_captured_at(text)
        if cap and (now - cap).days <= 7:
            recent.append(f"- {e.get('title', '')} ({e.get('section', '')})")

    if not recent:
        return {
            "status": "ok",
            "review": "No captures in the last 7 days.",
            "wins": [],
            "captures": [],
            "gaps": [],
            "next_focus": "Start capturing knowledge!",
        }

    task = (
        "You are a personal operating system assistant. Generate a weekly review based on these captures:\n\n"
        + "\n".join(recent[:20])
        + "\n\nFormat your response as JSON with keys: wins (list), captures_summary (string), "
        "gaps (list), next_focus (string). Be concise and actionable."
    )

    try:
        raw = run_agent(task=task)
        # Try to extract JSON
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("\n", 1)[0]
        cleaned = cleaned.strip()
        review_data = json.loads(cleaned)
    except Exception:
        review_data = {
            "wins": ["Kept the system running"],
            "captures_summary": f"Captured {len(recent)} entries this week.",
            "gaps": [],
            "next_focus": "Continue consistent capturing.",
        }

    return {
        "status": "ok",
        "review": review_data.get("captures_summary", ""),
        "wins": review_data.get("wins", []),
        "gaps": review_data.get("gaps", []),
        "next_focus": review_data.get("next_focus", ""),
        "recent_count": len(recent),
    }


@router.get("/planning/focus")
async def get_focus(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """AI-suggested priorities based on goals + recent activity."""
    goals = _read_planning_entries("goals")
    active_goals = [g for g in goals if g.get("status") == "active"]

    index = _load_index()
    entries = index.get("entries", [])
    now = datetime.now()

    recent_sections: dict[str, int] = {}
    for e in entries:
        path = _PROJECT_ROOT / e.get("path", "")
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        cap = _extract_captured_at(text)
        if cap and (now - cap).days <= 7:
            section = e.get("section", "unknown")
            recent_sections[section] = recent_sections.get(section, 0) + 1

    # Simple heuristic suggestion
    suggestions: list[str] = []
    if not active_goals:
        suggestions.append("No active goals. Consider setting one.")
    else:
        suggestions.append(f"You have {len(active_goals)} active goals.")

    if not recent_sections:
        suggestions.append("No captures this week. Time to add something to the library.")
    else:
        top_section = max(recent_sections, key=recent_sections.get)
        suggestions.append(f"Most active section: {top_section} ({recent_sections[top_section]} entries).")

    return {
        "status": "ok",
        "active_goals_count": len(active_goals),
        "active_goals": [g["title"] for g in active_goals],
        "recent_sections": recent_sections,
        "suggestions": suggestions,
    }
