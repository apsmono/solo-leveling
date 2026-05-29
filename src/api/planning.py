"""Planning REST endpoints — goals, projects, reviews, tasks."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.api.deps import require_auth
from src.agents.dispatcher import run_agent

router = APIRouter()

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LIBRARY_ROOT = _PROJECT_ROOT / "library"
_INDEX_PATH = _LIBRARY_ROOT / "index.json"

_PLANNING_SECTIONS = {"goals", "projects", "reviews", "tasks"}


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


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

class TaskCreate(BaseModel):
    title: str
    status: str = "active"
    goal_id: Optional[str] = None
    project_id: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    goal_id: Optional[str] = None
    project_id: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None


def _read_tasks(
    status: Optional[str] = None,
    goal_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Read tasks from library/tasks/ directory."""
    entries: list[dict[str, Any]] = []
    dir_path = _LIBRARY_ROOT / "tasks"
    if not dir_path.exists():
        return entries

    for path in sorted(dir_path.rglob("*.md")):
        if path.name == ".gitkeep":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        title = path.stem
        task_status = "active"
        task_goal_id: Optional[str] = None
        task_project_id: Optional[str] = None
        priority = "medium"
        due_date: Optional[str] = None
        captured_at: Optional[str] = None

        # Parse YAML frontmatter
        frontmatter_match = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if frontmatter_match:
            fm = frontmatter_match.group(1)
            title_match = re.search(r"^title:\s*(.+)$", fm, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip().strip('"').strip("'")
            status_match = re.search(r"^status:\s*(.+)$", fm, re.MULTILINE)
            if status_match:
                task_status = status_match.group(1).strip()
            goal_match = re.search(r"^goal_id:\s*(.*)$", fm, re.MULTILINE)
            if goal_match:
                val = goal_match.group(1).strip()
                if val and val.lower() != "null":
                    task_goal_id = val
            project_match = re.search(r"^project_id:\s*(.*)$", fm, re.MULTILINE)
            if project_match:
                val = project_match.group(1).strip()
                if val and val.lower() != "null":
                    task_project_id = val
            priority_match = re.search(r"^priority:\s*(.+)$", fm, re.MULTILINE)
            if priority_match:
                priority = priority_match.group(1).strip()
            due_match = re.search(r"^due_date:\s*(.*)$", fm, re.MULTILINE)
            if due_match:
                val = due_match.group(1).strip()
                if val and val.lower() != "null":
                    due_date = val
            cap_match = re.search(r"^created_at:\s*(.+)$", fm, re.MULTILINE)
            if cap_match:
                captured_at = cap_match.group(1).strip()

        entry = {
            "id": path.stem,
            "title": title,
            "status": task_status,
            "goal_id": task_goal_id,
            "project_id": task_project_id,
            "priority": priority,
            "due_date": due_date,
            "created_at": captured_at,
            "path": str(path.relative_to(_PROJECT_ROOT)),
        }

        # Apply filters
        if status and entry["status"] != status:
            continue
        if goal_id is not None and entry["goal_id"] != goal_id:
            continue
        if project_id is not None and entry["project_id"] != project_id:
            continue

        entries.append(entry)

    return entries


def _write_task(task_id: str, data: dict[str, Any]) -> None:
    """Write a task as a markdown file with YAML frontmatter."""
    dir_path = _LIBRARY_ROOT / "tasks"
    dir_path.mkdir(parents=True, exist_ok=True)
    path = dir_path / f"{task_id}.md"

    frontmatter_lines = ["---"]
    frontmatter_lines.append(f'title: "{data["title"]}"')
    frontmatter_lines.append(f"status: {data.get('status', 'active')}")
    frontmatter_lines.append(f"goal_id: {data.get('goal_id') or 'null'}")
    frontmatter_lines.append(f"project_id: {data.get('project_id') or 'null'}")
    frontmatter_lines.append(f"priority: {data.get('priority', 'medium')}")
    frontmatter_lines.append(f"due_date: {data.get('due_date') or 'null'}")
    frontmatter_lines.append(f"created_at: {data.get('created_at', datetime.now().isoformat())}")
    frontmatter_lines.append("---")

    body = data.get("body", "").strip()
    content = "\n".join(frontmatter_lines)
    if body:
        content += "\n\n" + body

    path.write_text(content, encoding="utf-8")


@router.get("/planning/tasks")
async def get_tasks(
    status: Optional[str] = None,
    goal_id: Optional[str] = None,
    project_id: Optional[str] = None,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    tasks = _read_tasks(status=status, goal_id=goal_id, project_id=project_id)
    return {
        "tasks": tasks,
        "active": [t for t in tasks if t.get("status") == "active"],
        "completed": [t for t in tasks if t.get("status") == "completed"],
        "by_priority": {
            "high": [t for t in tasks if t.get("priority") == "high"],
            "medium": [t for t in tasks if t.get("priority") == "medium"],
            "low": [t for t in tasks if t.get("priority") == "low"],
        },
    }


@router.post("/planning/tasks")
async def create_task(
    payload: TaskCreate,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    task_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    data = {
        "title": payload.title,
        "status": payload.status,
        "goal_id": payload.goal_id,
        "project_id": payload.project_id,
        "priority": payload.priority,
        "due_date": payload.due_date,
        "created_at": now,
    }
    _write_task(task_id, data)
    return {"status": "ok", "id": task_id, **data}


@router.put("/planning/tasks/{task_id}")
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    existing = _read_tasks()
    task = next((t for t in existing if t["id"] == task_id), None)
    if not task:
        return {"status": "error", "message": "Task not found"}

    # Read body if exists
    path = _LIBRARY_ROOT / "tasks" / f"{task_id}.md"
    body = ""
    if path.exists():
        text = path.read_text(encoding="utf-8", errors="ignore")
        frontmatter_match = re.search(r"^---\s*\n.*?\n---\s*(.*)$", text, re.DOTALL)
        if frontmatter_match:
            body = frontmatter_match.group(1).strip()

    data = {
        "title": payload.title if payload.title is not None else task["title"],
        "status": payload.status if payload.status is not None else task["status"],
        "goal_id": payload.goal_id if payload.goal_id is not None else task.get("goal_id"),
        "project_id": payload.project_id if payload.project_id is not None else task.get("project_id"),
        "priority": payload.priority if payload.priority is not None else task.get("priority", "medium"),
        "due_date": payload.due_date if payload.due_date is not None else task.get("due_date"),
        "created_at": task.get("created_at", datetime.now().isoformat()),
        "body": body,
    }
    _write_task(task_id, data)
    return {"status": "ok", "id": task_id, **data}


@router.delete("/planning/tasks/{task_id}")
async def delete_task(
    task_id: str,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    path = _LIBRARY_ROOT / "tasks" / f"{task_id}.md"
    if path.exists():
        path.unlink()
        return {"status": "ok", "id": task_id}
    return {"status": "error", "message": "Task not found"}


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
