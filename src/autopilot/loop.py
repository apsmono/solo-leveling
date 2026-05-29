"""
Autopilot execution loop.

Maintains task state and executes one step per tick.
The loop is AI-agnostic: it receives step plans from the planner,
executes tools through the registry, and records observations.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

from src.autopilot.governor import Governor, ResponsibilityLevel
from src.autopilot.planner import plan_steps
from src.autopilot.tools import ToolRegistry
from src.core.config import (
    AUTOPILOT_APPROVALS_PATH,
    AUTOPILOT_MAX_STEPS_PER_TASK,
    AUTOPILOT_RL_LEVEL,
    AUTOPILOT_STATE_PATH,
    AUTOPILOT_TASK_STORE_PATH,
)

logger = logging.getLogger(__name__)

_LOOP_LOCK = Lock()
_loop_instance: AutopilotLoop | None = None


class AutopilotLoop:
    """Main autopilot loop."""

    def __init__(self) -> None:
        self.registry = ToolRegistry()
        self.governor = Governor(current_rl=ResponsibilityLevel(AUTOPILOT_RL_LEVEL))
        self.task_store = _TaskStore(path=Path(AUTOPILOT_TASK_STORE_PATH))
        self.state_store = _StateStore(path=Path(AUTOPILOT_STATE_PATH))
        self.approval_store = _ApprovalStore(path=Path(AUTOPILOT_APPROVALS_PATH))

    def start_task(self, goal: str) -> dict[str, Any]:
        """Create a new autopilot task, plan it, and queue for execution."""
        task_id = _generate_task_id()
        steps = plan_steps(goal)
        task: dict[str, Any] = {
            "id": task_id,
            "goal": goal,
            "steps": steps,
            "status": "pending",
            "current_step": 0,
            "observations": [],
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
        }
        self.task_store.save(task)
        logger.info("Autopilot task %s created with %d steps", task_id, len(steps))
        return task

    def tick(self) -> None:
        """Execute one step of the active task. Called by the scheduler."""
        with _LOOP_LOCK:
            state = self.state_store.load()
            active_id = state.get("active_task_id")
            if not active_id:
                # Pick the oldest pending task
                pending = [t for t in self.task_store.list_all() if t.get("status") == "pending"]
                if not pending:
                    return
                pending.sort(key=lambda t: t.get("created_at", ""))
                task = pending[0]
                active_id = task["id"]
                state["active_task_id"] = active_id
                task["status"] = "in_progress"
                self.task_store.save(task)
                self.state_store.save(state)
                logger.info("Autopilot picked up task %s", active_id)

            task = self.task_store.load(active_id)
            if not task:
                logger.warning("Active task %s not found; clearing state.", active_id)
                state["active_task_id"] = None
                state["current_step"] = 0
                self.state_store.save(state)
                return

            if task.get("status") != "in_progress":
                # Task paused or completed; clear active
                state["active_task_id"] = None
                state["current_step"] = 0
                self.state_store.save(state)
                return

            current_step = state.get("current_step", 0)
            steps = task.get("steps", [])

            if current_step >= len(steps):
                # Done
                task["status"] = "completed"
                task["updated_at"] = _now_iso()
                self.task_store.save(task)
                state["active_task_id"] = None
                state["current_step"] = 0
                self.state_store.save(state)
                logger.info("Autopilot task %s completed", active_id)
                return

            if current_step >= AUTOPILOT_MAX_STEPS_PER_TASK:
                task["status"] = "failed"
                task["observations"].append(f"Exceeded max steps ({AUTOPILOT_MAX_STEPS_PER_TASK})")
                task["updated_at"] = _now_iso()
                self.task_store.save(task)
                state["active_task_id"] = None
                state["current_step"] = 0
                self.state_store.save(state)
                logger.warning("Autopilot task %s exceeded max steps", active_id)
                return

            step = steps[current_step]
            tool_name = step.get("tool", "")
            tool_args = step.get("args", {})

            allowed, reason = self.governor.can_execute(tool_name, tool_args)
            if not allowed:
                task["status"] = "awaiting_approval"
                task["observations"].append(f"Step {current_step} blocked: {reason}")
                task["updated_at"] = _now_iso()
                self.task_store.save(task)
                approval_id = self.approval_store.create(
                    task_id=active_id,
                    step=current_step,
                    tool=tool_name,
                    args=tool_args,
                    reason=reason,
                )
                logger.info("Autopilot task %s paused for approval at step %s (approval %s)", active_id, current_step, approval_id)
                return

            logger.info("Autopilot task %s executing step %s: %s", active_id, current_step, tool_name)
            observation = self.registry.execute(tool_name, tool_args)
            task["observations"].append(observation)
            task["updated_at"] = _now_iso()
            self.task_store.save(task)

            state["current_step"] = current_step + 1
            self.state_store.save(state)
            logger.info("Autopilot task %s step %s done", active_id, current_step)

    def approve_task(self, task_id: str) -> str:
        """Resume a task that was paused for approval."""
        task = self.task_store.load(task_id)
        if not task:
            return f"Task {task_id} not found."
        if task.get("status") != "awaiting_approval":
            return f"Task {task_id} is not awaiting approval (status: {task.get('status')})."
        task["status"] = "in_progress"
        task["updated_at"] = _now_iso()
        self.task_store.save(task)
        self.approval_store.resolve(task_id)
        logger.info("Autopilot task %s approved and resumed", task_id)
        return f"Task {task_id} approved and resumed."

    def approve_approval(self, approval_id: str) -> str:
        """Approve a specific approval request and resume its task."""
        approval = self.approval_store.get(approval_id)
        if not approval:
            return f"Approval {approval_id} not found."
        if approval.get("status") != "pending":
            return f"Approval {approval_id} is already {approval.get('status')}."

        task_id = approval["task_id"]
        self.approval_store.approve_by_id(approval_id)

        task = self.task_store.load(task_id)
        if task and task.get("status") == "awaiting_approval":
            task["status"] = "in_progress"
            task["updated_at"] = _now_iso()
            self.task_store.save(task)
            logger.info("Autopilot task %s approved via approval %s and resumed", task_id, approval_id)
            return f"Approval {approval_id} approved. Task {task_id} resumed."
        return f"Approval {approval_id} approved."

    def reject_approval(self, approval_id: str) -> str:
        """Reject a specific approval request and fail its task."""
        approval = self.approval_store.get(approval_id)
        if not approval:
            return f"Approval {approval_id} not found."
        if approval.get("status") != "pending":
            return f"Approval {approval_id} is already {approval.get('status')}."

        task_id = approval["task_id"]
        self.approval_store.reject_by_id(approval_id)

        task = self.task_store.load(task_id)
        if task and task.get("status") == "awaiting_approval":
            task["status"] = "failed"
            task["observations"].append(f"Approval {approval_id} rejected by user.")
            task["updated_at"] = _now_iso()
            self.task_store.save(task)
            state = self.state_store.load()
            if state.get("active_task_id") == task_id:
                state["active_task_id"] = None
                state["current_step"] = 0
                self.state_store.save(state)
            logger.info("Autopilot task %s rejected via approval %s", task_id, approval_id)
            return f"Approval {approval_id} rejected. Task {task_id} marked as failed."
        return f"Approval {approval_id} rejected."

    def pause_task(self, task_id: str) -> str:
        task = self.task_store.load(task_id)
        if not task:
            return f"Task {task_id} not found."
        if task.get("status") == "in_progress":
            task["status"] = "paused"
            task["updated_at"] = _now_iso()
            self.task_store.save(task)
            state = self.state_store.load()
            if state.get("active_task_id") == task_id:
                state["active_task_id"] = None
                self.state_store.save(state)
            return f"Task {task_id} paused."
        return f"Task {task_id} is already {task.get('status')}."

    def get_status(self) -> str:
        tasks = self.task_store.list_all()
        if not tasks:
            return "No autopilot tasks."
        lines = ["Autopilot tasks:"]
        for t in tasks:
            lines.append(
                f"• {t['id']}: {t['status']} | {t.get('current_step', 0)}/{len(t.get('steps', []))} steps | {t['goal'][:60]}"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

class _TaskStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _load_all(self) -> dict[str, dict[str, Any]]:
        if not self.path.exists():
            return {}
        try:
            raw = self.path.read_text(encoding="utf-8").strip()
            if not raw:
                return {}
            return json.loads(raw)
        except (json.JSONDecodeError, OSError):
            logger.warning("Task store unreadable; returning empty.")
            return {}

    def _save_all(self, data: dict[str, dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._load_all().values())

    def load(self, task_id: str) -> dict[str, Any] | None:
        return self._load_all().get(task_id)

    def save(self, task: dict[str, Any]) -> None:
        data = self._load_all()
        data[task["id"]] = task
        self._save_all(data)


class _StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"active_task_id": None, "current_step": 0}
        try:
            raw = self.path.read_text(encoding="utf-8").strip()
            if not raw:
                return {"active_task_id": None, "current_step": 0}
            return json.loads(raw)
        except (json.JSONDecodeError, OSError):
            return {"active_task_id": None, "current_step": 0}

    def save(self, state: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(state, indent=2), encoding="utf-8")


class _ApprovalStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _load_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            raw = self.path.read_text(encoding="utf-8").strip()
            if not raw:
                return []
            loaded = json.loads(raw)
            return loaded if isinstance(loaded, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def _save_all(self, data: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def create(self, task_id: str, step: int, tool: str, args: dict[str, Any], reason: str) -> str:
        items = self._load_all()
        approval_id = _generate_task_id()
        items.append(
            {
                "id": approval_id,
                "task_id": task_id,
                "step": step,
                "tool": tool,
                "args": args,
                "reason": reason,
                "status": "pending",
                "created_at": _now_iso(),
            }
        )
        self._save_all(items)
        return approval_id

    def get(self, approval_id: str) -> dict[str, Any] | None:
        items = self._load_all()
        for item in items:
            if item.get("id") == approval_id:
                return item
        return None

    def approve_by_id(self, approval_id: str) -> bool:
        items = self._load_all()
        for item in items:
            if item.get("id") == approval_id and item.get("status") == "pending":
                item["status"] = "approved"
                item["resolved_at"] = _now_iso()
                self._save_all(items)
                return True
        return False

    def reject_by_id(self, approval_id: str) -> bool:
        items = self._load_all()
        for item in items:
            if item.get("id") == approval_id and item.get("status") == "pending":
                item["status"] = "rejected"
                item["resolved_at"] = _now_iso()
                self._save_all(items)
                return True
        return False

    def resolve(self, task_id: str) -> None:
        items = self._load_all()
        for item in items:
            if item.get("task_id") == task_id and item.get("status") == "pending":
                item["status"] = "approved"
                item["resolved_at"] = _now_iso()
        self._save_all(items)


def _generate_task_id() -> str:
    from uuid import uuid4

    return uuid4().hex[:12]


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def get_loop() -> AutopilotLoop:
    global _loop_instance
    if _loop_instance is None:
        _loop_instance = AutopilotLoop()
    return _loop_instance
