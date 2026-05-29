from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.app import app
from src.autopilot.governor import Governor, ResponsibilityLevel
from src.autopilot.loop import AutopilotLoop
from src.autopilot.tools import ToolRegistry


class GovernorTests(unittest.TestCase):
    def test_rl1_can_read(self) -> None:
        gov = Governor(ResponsibilityLevel.ASSISTED)
        allowed, reason = gov.can_execute("read", {"path": "README.md"})
        self.assertTrue(allowed)
        self.assertEqual(reason, "")

    def test_rl1_cannot_bash(self) -> None:
        gov = Governor(ResponsibilityLevel.ASSISTED)
        allowed, reason = gov.can_execute("bash", {"command": "ls"})
        self.assertFalse(allowed)
        self.assertIn("requires RL2", reason)

    def test_rl3_can_git_commit(self) -> None:
        gov = Governor(ResponsibilityLevel.CROSS_MODULE)
        allowed, _ = gov.can_execute("git_commit", {"message": "test"})
        self.assertTrue(allowed)

    def test_dangerous_bash_blocked(self) -> None:
        gov = Governor(ResponsibilityLevel.PROGRAM_LEAD)
        allowed, reason = gov.can_execute("bash", {"command": "rm -rf /"})
        self.assertFalse(allowed)
        self.assertIn("sandbox", reason)

    def test_unknown_tool_defaults_to_rl5(self) -> None:
        gov = Governor(ResponsibilityLevel.LEAD_EXECUTOR)
        allowed, reason = gov.can_execute("nuke_everything", {})
        self.assertFalse(allowed)
        self.assertIn("RL5", reason)


class ToolRegistryTests(unittest.TestCase):
    def test_read_tool(self) -> None:
        reg = ToolRegistry()
        result = reg.execute("read", {"path": "README.md", "limit": 5})
        self.assertIn("---", result)

    def test_read_outside_repo_blocked(self) -> None:
        reg = ToolRegistry()
        result = reg.execute("read", {"path": "/etc/passwd"})
        self.assertIn("outside the repository", result)

    def test_bash_echo(self) -> None:
        reg = ToolRegistry()
        result = reg.execute("bash", {"command": "echo hello"})
        self.assertIn("hello", result)

    def test_unknown_tool(self) -> None:
        reg = ToolRegistry()
        result = reg.execute("fly", {})
        self.assertIn("unknown tool", result)


class AutopilotLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.tasks_path = Path(self.tmpdir.name) / "tasks.json"
        self.state_path = Path(self.tmpdir.name) / "state.json"
        self.approvals_path = Path(self.tmpdir.name) / "approvals.json"

        patcher_tasks = patch("src.autopilot.loop.AUTOPILOT_TASK_STORE_PATH", str(self.tasks_path))
        patcher_state = patch("src.autopilot.loop.AUTOPILOT_STATE_PATH", str(self.state_path))
        patcher_approvals = patch("src.autopilot.loop.AUTOPILOT_APPROVALS_PATH", str(self.approvals_path))
        patcher_max_steps = patch("src.autopilot.loop.AUTOPILOT_MAX_STEPS_PER_TASK", 10)
        patcher_rl = patch("src.autopilot.loop.AUTOPILOT_RL_LEVEL", 5)

        patcher_tasks.start()
        patcher_state.start()
        patcher_approvals.start()
        patcher_max_steps.start()
        patcher_rl.start()

        self.addCleanup(patcher_tasks.stop)
        self.addCleanup(patcher_state.stop)
        self.addCleanup(patcher_approvals.stop)
        self.addCleanup(patcher_max_steps.stop)
        self.addCleanup(patcher_rl.stop)

        self.loop = AutopilotLoop()

    @patch("src.autopilot.loop.plan_steps", return_value=[{"tool": "read", "args": {"path": "README.md"}, "reason": "test"}])
    def test_start_task(self, _mock_plan: object) -> None:
        task = self.loop.start_task("test goal")
        self.assertEqual(task["goal"], "test goal")
        self.assertEqual(task["status"], "pending")
        self.assertIn("id", task)
        # Clean up singleton so other tests see empty state
        from src.autopilot import loop as loop_mod
        loop_mod._loop_instance = None

    def test_status_empty(self) -> None:
        # Ensure singleton is clean
        from src.autopilot import loop as loop_mod
        loop_mod._loop_instance = None
        result = self.loop.get_status()
        self.assertIn("No autopilot tasks", result)

    def test_approve_nonexistent_task(self) -> None:
        result = self.loop.approve_task("nosuchid")
        self.assertIn("not found", result)

    def test_pause_nonexistent_task(self) -> None:
        result = self.loop.pause_task("nosuchid")
        self.assertIn("not found", result)

    @patch("src.autopilot.loop.plan_steps", return_value=[{"tool": "read", "args": {"path": "README.md"}, "reason": "test"}])
    def test_task_store_persistence(self, _mock_plan: object) -> None:
        task = self.loop.start_task("persistent goal")
        loaded = self.loop.task_store.load(task["id"])
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["goal"], "persistent goal")


class RouterAutopilotIntentTests(unittest.TestCase):
    def setUp(self) -> None:
        from src.autopilot import loop as loop_mod
        loop_mod._loop_instance = None
        # Wipe default autopilot stores so no stale tasks leak between test runs
        from src.core.config import (
            AUTOPILOT_TASK_STORE_PATH,
            AUTOPILOT_STATE_PATH,
            AUTOPILOT_APPROVALS_PATH,
        )
        for p in (AUTOPILOT_TASK_STORE_PATH, AUTOPILOT_STATE_PATH, AUTOPILOT_APPROVALS_PATH):
            try:
                Path(p).unlink()
            except FileNotFoundError:
                pass

    def test_help_includes_autopilot(self) -> None:
        from src.core.router import route_command

        result = route_command("help")
        self.assertIn("autopilot start", result)
        self.assertIn("autopilot status", result)

    def test_autopilot_status_no_tasks(self) -> None:
        from src.core.router import route_command

        result = route_command("autopilot status")
        self.assertIn("No autopilot tasks", result)


class WriteToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.reg = ToolRegistry()
        self.cwd_patcher = patch("src.autopilot.tools.Path.cwd", return_value=Path(self.tmpdir.name))
        self.cwd_patcher.start()
        self.addCleanup(self.cwd_patcher.stop)

    def test_write_creates_file(self) -> None:
        path = Path(self.tmpdir.name) / "test.txt"
        result = self.reg.execute("write", {"path": str(path), "content": "hello world"})
        self.assertIn("Wrote", result)
        self.assertTrue(path.exists())
        self.assertEqual(path.read_text(), "hello world")

    def test_write_appends_file(self) -> None:
        path = Path(self.tmpdir.name) / "test.txt"
        path.write_text("hello ")
        result = self.reg.execute("write", {"path": str(path), "content": "world", "mode": "append"})
        self.assertIn("Appended", result)
        self.assertEqual(path.read_text(), "hello world")

    def test_write_outside_repo_blocked(self) -> None:
        result = self.reg.execute("write", {"path": "/etc/passwd", "content": "x"})
        self.assertIn("outside the repository", result)

    def test_write_invalid_mode(self) -> None:
        path = Path(self.tmpdir.name) / "test.txt"
        result = self.reg.execute("write", {"path": str(path), "content": "x", "mode": "invalid"})
        self.assertIn("invalid mode", result)


class ClaudeCodeToolTests(unittest.TestCase):
    @patch("src.autopilot.tools.shutil.which")
    @patch("src.agents.dispatcher.run_agent")
    def test_claude_code_fallback_when_binary_missing(self, mock_run_agent: MagicMock, mock_which: MagicMock) -> None:
        mock_which.return_value = None
        mock_run_agent.return_value = "fallback response"
        reg = ToolRegistry()
        result = reg.execute("claude_code", {"prompt": "write a hello world in python"})
        self.assertEqual(result, "fallback response")
        mock_run_agent.assert_called_once()

    @patch("src.autopilot.tools.shutil.which")
    def test_claude_code_runs_binary_when_available(self, mock_which: MagicMock) -> None:
        mock_which.return_value = "/usr/local/bin/claude"
        reg = ToolRegistry()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="claude output", stderr="", returncode=0)
            result = reg.execute("claude_code", {"prompt": "test"})
            self.assertIn("claude output", result)
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            self.assertEqual(args[0], ["/usr/local/bin/claude", "-p", "test"])
            self.assertFalse(kwargs.get("shell", False))

    @patch("src.autopilot.tools.shutil.which")
    def test_claude_code_timeout(self, mock_which: MagicMock) -> None:
        mock_which.return_value = "/usr/local/bin/claude"
        reg = ToolRegistry()
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=30)
            result = reg.execute("claude_code", {"prompt": "test", "timeout": 30})
            self.assertIn("timed out", result)


class GovernorNewToolTests(unittest.TestCase):
    def test_rl2_can_write(self) -> None:
        gov = Governor(ResponsibilityLevel.INDEPENDENT)
        allowed, _ = gov.can_execute("write", {"path": "test.py", "content": "x"})
        self.assertTrue(allowed)

    def test_rl1_cannot_write(self) -> None:
        gov = Governor(ResponsibilityLevel.ASSISTED)
        allowed, reason = gov.can_execute("write", {"path": "test.py", "content": "x"})
        self.assertFalse(allowed)
        self.assertIn("requires RL2", reason)

    def test_rl3_can_claude_code(self) -> None:
        gov = Governor(ResponsibilityLevel.CROSS_MODULE)
        allowed, _ = gov.can_execute("claude_code", {"prompt": "test"})
        self.assertTrue(allowed)

    def test_rl2_cannot_claude_code(self) -> None:
        gov = Governor(ResponsibilityLevel.INDEPENDENT)
        allowed, reason = gov.can_execute("claude_code", {"prompt": "test"})
        self.assertFalse(allowed)
        self.assertIn("requires RL3", reason)


class AutopilotApprovalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.tasks_path = Path(self.tmpdir.name) / "tasks.json"
        self.state_path = Path(self.tmpdir.name) / "state.json"
        self.approvals_path = Path(self.tmpdir.name) / "approvals.json"

        patcher_tasks = patch("src.autopilot.loop.AUTOPILOT_TASK_STORE_PATH", str(self.tasks_path))
        patcher_state = patch("src.autopilot.loop.AUTOPILOT_STATE_PATH", str(self.state_path))
        patcher_approvals = patch("src.autopilot.loop.AUTOPILOT_APPROVALS_PATH", str(self.approvals_path))
        patcher_max_steps = patch("src.autopilot.loop.AUTOPILOT_MAX_STEPS_PER_TASK", 10)
        patcher_rl = patch("src.autopilot.loop.AUTOPILOT_RL_LEVEL", 5)

        patcher_tasks.start()
        patcher_state.start()
        patcher_approvals.start()
        patcher_max_steps.start()
        patcher_rl.start()

        self.addCleanup(patcher_tasks.stop)
        self.addCleanup(patcher_state.stop)
        self.addCleanup(patcher_approvals.stop)
        self.addCleanup(patcher_max_steps.stop)
        self.addCleanup(patcher_rl.stop)

        self.loop = AutopilotLoop()

    @patch("src.autopilot.loop.plan_steps", return_value=[])
    def test_approve_approval_by_id(self, _mock_plan: object) -> None:
        task = self.loop.start_task("test goal")
        # Manually create an approval
        approval_id = self.loop.approval_store.create(task["id"], 0, "bash", {"command": "ls"}, "test reason")
        task["status"] = "awaiting_approval"
        self.loop.task_store.save(task)

        result = self.loop.approve_approval(approval_id)
        self.assertIn("approved", result)
        self.assertIn("resumed", result)

        loaded = self.loop.task_store.load(task["id"])
        self.assertEqual(loaded["status"], "in_progress")

    @patch("src.autopilot.loop.plan_steps", return_value=[])
    def test_reject_approval_by_id(self, _mock_plan: object) -> None:
        task = self.loop.start_task("test goal")
        approval_id = self.loop.approval_store.create(task["id"], 0, "bash", {"command": "ls"}, "test reason")
        task["status"] = "awaiting_approval"
        self.loop.task_store.save(task)

        result = self.loop.reject_approval(approval_id)
        self.assertIn("rejected", result)
        self.assertIn("failed", result)

        loaded = self.loop.task_store.load(task["id"])
        self.assertEqual(loaded["status"], "failed")


class AutopilotApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}

    @patch("src.api.deps.verify_id_token")
    @patch("src.autopilot.loop.plan_steps", return_value=[])
    def test_create_task(self, _mock_plan: MagicMock, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.post("/api/v1/autopilot/tasks", json={"goal": "test goal"}, headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("task", data)
        self.assertEqual(data["task"]["goal"], "test goal")

    @patch("src.api.deps.verify_id_token")
    def test_list_tasks(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/autopilot/tasks", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("tasks", data)
        self.assertIsInstance(data["tasks"], list)

    @patch("src.api.deps.verify_id_token")
    def test_get_task_not_found(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/autopilot/tasks/nosuchid", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsNone(data["task"])

    @patch("src.api.deps.verify_id_token")
    def test_list_approvals(self, mock_verify: MagicMock) -> None:
        mock_verify.return_value = self.mock_user
        res = self.client.get("/api/v1/autopilot/approvals", headers={"Authorization": "Bearer valid-token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("approvals", data)
        self.assertIsInstance(data["approvals"], list)

    @patch("src.api.deps.verify_id_token")
    def test_unauthorized_without_token(self, mock_verify: MagicMock) -> None:
        mock_verify.side_effect = HTTPException(status_code=401, detail="Unauthorized")
        res = self.client.get("/api/v1/autopilot/tasks")
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
