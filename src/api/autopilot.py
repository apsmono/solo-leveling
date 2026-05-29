"""Autopilot task and approval REST API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from src.api.deps import require_auth
from src.autopilot.loop import get_loop

router = APIRouter()


@router.get("/autopilot/tasks")
async def list_tasks(_: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    tasks = get_loop().task_store.list_all()
    tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)
    return {"tasks": tasks}


@router.get("/autopilot/tasks/{task_id}")
async def get_task(task_id: str, _: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
    task = get_loop().task_store.load(task_id)
    return {"task": task}


@router.post("/autopilot/tasks")
async def create_task(
    body: dict[str, Any],
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    goal = body.get("goal", "").strip()
    if not goal:
        return {"status": "error", "message": "Missing 'goal' field."}
    task = get_loop().start_task(goal)
    return {"status": "ok", "task": task}


@router.post("/autopilot/tasks/{task_id}/approve")
async def approve_task(
    task_id: str,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    message = get_loop().approve_task(task_id)
    return {"status": "ok", "message": message}


@router.post("/autopilot/tasks/{task_id}/pause")
async def pause_task(
    task_id: str,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    message = get_loop().pause_task(task_id)
    return {"status": "ok", "message": message}


@router.get("/autopilot/approvals")
async def list_approvals(
    status: str = Query(default="pending"),
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    approvals = get_loop().approval_store._load_all()
    if status != "all":
        approvals = [a for a in approvals if a.get("status") == status]
    approvals.sort(key=lambda a: a.get("created_at", ""), reverse=True)
    return {"approvals": approvals}


@router.post("/autopilot/approvals/{approval_id}/approve")
async def approve_approval(
    approval_id: str,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    message = get_loop().approve_approval(approval_id)
    return {"status": "ok", "message": message}


@router.post("/autopilot/approvals/{approval_id}/reject")
async def reject_approval(
    approval_id: str,
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    message = get_loop().reject_approval(approval_id)
    return {"status": "ok", "message": message}
