from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_status_empty(self) -> None:
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
    def test_help_includes_autopilot(self) -> None:
        from src.core.router import route_command

        result = route_command("help")
        self.assertIn("autopilot start", result)
        self.assertIn("autopilot status", result)

    def test_autopilot_status_no_tasks(self) -> None:
        from src.core.router import route_command

        result = route_command("autopilot status")
        self.assertIn("No autopilot tasks", result)


if __name__ == "__main__":
    unittest.main()
