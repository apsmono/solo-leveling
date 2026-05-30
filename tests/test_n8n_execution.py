"""Tests for the n8n execution layer (Phase 2).

Wave 1 (plan 02-01) ships N8NClientTests and ErrorTests green. The remaining
four classes are stubbed and completed to green in plan 02-03 (Wave 3).
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch


def _mock_httpx(mock_client_cls: MagicMock, payload: dict | None = None) -> MagicMock:
    """Wire a mocked httpx.Client context manager and return the inner client."""
    inner = MagicMock()
    response = MagicMock()
    response.json.return_value = payload if payload is not None else {}
    response.content = b"{}"
    response.raise_for_status.return_value = None
    inner.request.return_value = response
    mock_client_cls.return_value.__enter__.return_value = inner
    return inner


class N8NClientTests(unittest.TestCase):
    @patch("src.n8n.client.N8N_API_KEY", "test-key")
    @patch("src.n8n.client.httpx.Client")
    def test_headers_contains_api_key(self, mock_client_cls: MagicMock) -> None:
        from src.n8n import client as n8n

        headers = n8n._headers()
        self.assertIn("X-N8N-API-KEY", headers)
        self.assertEqual(headers["X-N8N-API-KEY"], "test-key")

    @patch("src.n8n.client.N8N_API_KEY", "")
    def test_missing_api_key_raises(self) -> None:
        from src.n8n import client as n8n

        with self.assertRaises(EnvironmentError):
            n8n._request("GET", "/workflows", params={"limit": 1})

    @patch("src.n8n.client.N8N_API_KEY", "test-key")
    @patch("src.n8n.client.httpx.Client")
    def test_trigger_workflow(self, mock_client_cls: MagicMock) -> None:
        inner = _mock_httpx(mock_client_cls, {"executionId": "7"})
        from src.n8n import client as n8n

        n8n.trigger_workflow(123, data={"key": "val"})
        args, kwargs = inner.request.call_args
        self.assertEqual(args[0], "POST")
        self.assertTrue(args[1].endswith("/api/v1/workflows/123/run"))
        self.assertEqual(kwargs["json"], {"data": {"key": "val"}})

    @patch("src.n8n.client.N8N_API_KEY", "test-key")
    @patch("src.n8n.client.httpx.Client")
    def test_get_execution(self, mock_client_cls: MagicMock) -> None:
        inner = _mock_httpx(mock_client_cls, {"id": "42"})
        from src.n8n import client as n8n

        n8n.get_execution(42)
        args, _ = inner.request.call_args
        self.assertEqual(args[0], "GET")
        self.assertTrue(args[1].endswith("/api/v1/executions/42"))

    @patch("src.n8n.client.N8N_API_KEY", "test-key")
    @patch("src.n8n.client.httpx.Client")
    def test_list_executions(self, mock_client_cls: MagicMock) -> None:
        inner = _mock_httpx(mock_client_cls, {"data": [{"id": "1"}]})
        from src.n8n import client as n8n

        result = n8n.list_executions(workflow_id=1, status="success", limit=5)
        args, kwargs = inner.request.call_args
        self.assertEqual(args[0], "GET")
        self.assertTrue(args[1].endswith("/api/v1/executions"))
        self.assertEqual(kwargs["params"]["workflowId"], 1)
        self.assertEqual(kwargs["params"]["status"], "success")
        self.assertEqual(kwargs["params"]["limit"], 5)
        self.assertEqual(result, [{"id": "1"}])

    @patch("src.n8n.client.N8N_API_KEY", "test-key")
    @patch("src.n8n.client.httpx.Client")
    def test_create_credential(self, mock_client_cls: MagicMock) -> None:
        inner = _mock_httpx(mock_client_cls, {"id": 9})
        from src.n8n import client as n8n

        n8n.create_credential("test-cred", "gmailOAuth2", {"clientId": "x"})
        args, kwargs = inner.request.call_args
        self.assertEqual(args[0], "POST")
        self.assertTrue(args[1].endswith("/api/v1/credentials"))
        self.assertEqual(kwargs["json"]["name"], "test-cred")
        self.assertEqual(kwargs["json"]["type"], "gmailOAuth2")

    @patch("src.n8n.client.N8N_API_KEY", "test-key")
    @patch("src.n8n.client.httpx.Client")
    def test_update_credential(self, mock_client_cls: MagicMock) -> None:
        inner = _mock_httpx(mock_client_cls, {"id": 1})
        from src.n8n import client as n8n

        n8n.update_credential(1, "test-cred", "gmailOAuth2", {"clientId": "x"})
        args, _ = inner.request.call_args
        self.assertEqual(args[0], "PUT")
        self.assertTrue(args[1].endswith("/api/v1/credentials/1"))

    @patch("src.n8n.client.N8N_API_KEY", "test-key")
    @patch("src.n8n.client.httpx.Client")
    def test_delete_credential(self, mock_client_cls: MagicMock) -> None:
        inner = _mock_httpx(mock_client_cls, {})
        from src.n8n import client as n8n

        n8n.delete_credential(1)
        args, _ = inner.request.call_args
        self.assertEqual(args[0], "DELETE")
        self.assertTrue(args[1].endswith("/api/v1/credentials/1"))

    @patch("src.n8n.client.N8N_API_KEY", "test-key")
    @patch("src.n8n.client.httpx.Client")
    def test_list_credentials(self, mock_client_cls: MagicMock) -> None:
        inner = _mock_httpx(mock_client_cls, {"data": [{"id": 1}]})
        from src.n8n import client as n8n

        result = n8n.list_credentials()
        args, _ = inner.request.call_args
        self.assertEqual(args[0], "GET")
        self.assertTrue(args[1].endswith("/api/v1/credentials"))
        self.assertEqual(result, [{"id": 1}])

    @patch("src.n8n.client.N8N_API_KEY", "test-key")
    @patch("src.n8n.client.httpx.Client")
    def test_health_check_ok(self, mock_client_cls: MagicMock) -> None:
        _mock_httpx(mock_client_cls, {"data": []})
        from src.n8n import client as n8n

        self.assertEqual(n8n.health_check(), {"ok": True})

    @patch("src.n8n.client.N8N_API_KEY", "")
    def test_health_check_no_key(self) -> None:
        from src.n8n import client as n8n

        result = n8n.health_check()
        self.assertFalse(result["ok"])
        self.assertIn("N8N_API_KEY", result["error"])


class ErrorTests(unittest.TestCase):
    def test_classify_credential_expired(self) -> None:
        from src.n8n.errors import ErrorClass, classify_error

        self.assertEqual(
            classify_error({"error": "token expired"}), ErrorClass.CREDENTIAL_EXPIRED
        )
        self.assertEqual(
            classify_error({"error": "invalid_grant"}), ErrorClass.CREDENTIAL_EXPIRED
        )

    def test_classify_credential_revoked(self) -> None:
        from src.n8n.errors import ErrorClass, classify_error

        self.assertEqual(
            classify_error({"error": "token has been revoked"}),
            ErrorClass.CREDENTIAL_REVOKED,
        )

    def test_classify_n8n_unreachable(self) -> None:
        from src.n8n.errors import ErrorClass, classify_error

        self.assertEqual(
            classify_error({"error": "ECONNREFUSED"}), ErrorClass.N8N_UNREACHABLE
        )

    def test_classify_workflow_not_found(self) -> None:
        from src.n8n.errors import ErrorClass, classify_error

        self.assertEqual(
            classify_error({"error": "workflow not found"}),
            ErrorClass.WORKFLOW_NOT_FOUND,
        )

    def test_classify_rate_limited(self) -> None:
        from src.n8n.errors import ErrorClass, classify_error

        self.assertEqual(
            classify_error({"error": "429 too many requests"}),
            ErrorClass.RATE_LIMITED,
        )

    def test_classify_unknown(self) -> None:
        from src.n8n.errors import ErrorClass, classify_error

        self.assertEqual(
            classify_error({"error": "something else"}), ErrorClass.UNKNOWN
        )

    def test_soft_message_no_stack_trace(self) -> None:
        from src.n8n.errors import ErrorClass, soft_error_message

        msg = soft_error_message(ErrorClass.CREDENTIAL_EXPIRED, integration="gmail")
        self.assertIn("expired", msg)
        self.assertIn("reconnect", msg.lower())
        self.assertNotIn("Traceback", msg)
        self.assertNotIn("Exception", msg)

    def test_soft_message_includes_integration(self) -> None:
        from src.n8n.errors import ErrorClass, soft_error_message

        msg = soft_error_message(ErrorClass.CREDENTIAL_REVOKED, integration="gmail")
        self.assertIn("Gmail", msg)

    def test_soft_message_unreachable(self) -> None:
        from src.n8n.errors import ErrorClass, soft_error_message

        self.assertIn("responding", soft_error_message(ErrorClass.N8N_UNREACHABLE))


class CredentialTests(unittest.TestCase):
    @patch("src.n8n.client.list_credentials", return_value=[])
    @patch("src.n8n.client.create_credential", return_value={"id": 9})
    def test_sync_creates_credential(
        self, mock_create: MagicMock, _mock_list: MagicMock
    ) -> None:
        from src.n8n.credentials import sync_credential

        cred_id = sync_credential(
            "gmail", {"client_id": "c", "client_secret": "s", "access_token": "a"},
            owner_id="test",
        )
        mock_create.assert_called_once()
        self.assertEqual(cred_id, 9)

    @patch(
        "src.n8n.client.list_credentials",
        return_value=[{"id": 1, "name": "signal-test-gmail"}],
    )
    @patch("src.n8n.client.update_credential", return_value={"id": 1})
    def test_sync_updates_existing(
        self, mock_update: MagicMock, _mock_list: MagicMock
    ) -> None:
        from src.n8n.credentials import sync_credential

        cred_id = sync_credential("gmail", {"access_token": "a"}, owner_id="test")
        mock_update.assert_called_once()
        self.assertEqual(cred_id, 1)

    def test_gmail_token_mapping(self) -> None:
        from src.n8n.credentials import _map_token_to_n8n_credential

        r = _map_token_to_n8n_credential(
            "gmail",
            {"client_id": "c", "client_secret": "s", "access_token": "a", "refresh_token": "r"},
        )
        self.assertIn("clientId", r)
        self.assertIn("clientSecret", r)
        self.assertIn("oauthTokenData", r)

    def test_github_token_mapping(self) -> None:
        from src.n8n.credentials import _map_token_to_n8n_credential

        r = _map_token_to_n8n_credential("github", {"access_token": "x"})
        self.assertIn("accessToken", r)

    def test_unknown_integration_raises(self) -> None:
        from src.n8n.credentials import sync_credential

        with self.assertRaises(ValueError):
            sync_credential("not_a_real_integration", {}, owner_id="test")


class TemplateTests(unittest.TestCase):
    def test_load_all_templates(self) -> None:
        from src.n8n.templates import load_all_templates

        templates = load_all_templates()
        self.assertEqual(len(templates), 2)
        ids = {t["id"] for t in templates}
        self.assertIn("gmail_read_summary", ids)
        self.assertIn("gmail_send_draft", ids)

    def test_match_template_match(self) -> None:
        from src.n8n.templates import match_template

        m = match_template("summarize my gmail")
        self.assertIsNotNone(m)
        self.assertEqual(m["id"], "gmail_read_summary")

    def test_match_template_no_match(self) -> None:
        from src.n8n.templates import match_template

        self.assertIsNone(match_template("xyzzy completely unknown intent"))

    def test_fill_parameters(self) -> None:
        from src.n8n.templates import fill_parameters

        skeleton = {"parameter_schema": {"max_messages": {"default": 5}}}
        result = fill_parameters(skeleton, {"max_messages": 10})
        self.assertEqual(result["max_messages"], 10)


class ExecutorTests(unittest.TestCase):
    def _run(self, coro):
        import asyncio

        return asyncio.run(coro)

    def test_no_template_match_declines(self) -> None:
        with patch("src.n8n.executor.n8n_templates.match_template", return_value=None), patch(
            "src.n8n.executor._log_unmet_intent"
        ) as mock_log:
            from src.n8n.executor import execute_intent

            result = self._run(execute_intent("unknown xyzzy", {}))
            self.assertEqual(result["status"], "declined")
            mock_log.assert_called_once()

    def test_execute_intent_side_effecting_needs_approval_at_rl1(self) -> None:
        skeleton = {
            "id": "gmail_send_draft",
            "name": "Gmail Send Draft",
            "integration": "gmail",
            "side_effecting": True,
            "description": "send",
            "n8n_workflow_id": 1,
            "parameter_schema": {},
        }
        with patch(
            "src.n8n.executor.n8n_templates.match_template", return_value=skeleton
        ), patch("src.n8n.executor._fill_with_llm", return_value={}), patch(
            "src.n8n.executor.AUTOPILOT_RL_LEVEL", 1
        ):
            from src.n8n.executor import execute_intent

            result = self._run(execute_intent("send an email", {}))
            self.assertEqual(result["status"], "needs_approval")

    def test_execute_intent_readonly(self) -> None:
        skeleton = {
            "id": "gmail_read_summary",
            "name": "Gmail Read Summary",
            "integration": "gmail",
            "side_effecting": False,
            "n8n_workflow_id": 5,
            "parameter_schema": {},
        }
        with patch(
            "src.n8n.executor.n8n_templates.match_template", return_value=skeleton
        ), patch("src.n8n.executor._fill_with_llm", return_value={}), patch(
            "src.n8n.executor.n8n_creds.sync_credential", return_value=1
        ), patch(
            "src.n8n.executor.n8n_client.trigger_workflow",
            return_value={"executionId": "1"},
        ), patch(
            "src.n8n.executor.n8n_client.get_execution",
            return_value={"status": "success", "finished": True},
        ):
            from src.n8n.executor import execute_intent

            result = self._run(execute_intent("summarize my gmail", {}))
            self.assertEqual(result["status"], "ok")

    def test_credential_synced_before_trigger(self) -> None:
        order: list[str] = []
        skeleton = {
            "id": "gmail_read_summary",
            "name": "Gmail Read Summary",
            "integration": "gmail",
            "side_effecting": False,
            "n8n_workflow_id": 5,
            "parameter_schema": {},
        }

        def sync_side(*_a, **_k):
            order.append("sync")
            return 1

        def trig_side(*_a, **_k):
            order.append("trigger")
            return {"executionId": "1"}

        with patch(
            "src.n8n.executor.n8n_templates.match_template", return_value=skeleton
        ), patch("src.n8n.executor._fill_with_llm", return_value={}), patch(
            "src.n8n.executor.n8n_creds.sync_credential", side_effect=sync_side
        ), patch(
            "src.n8n.executor.n8n_client.trigger_workflow", side_effect=trig_side
        ), patch(
            "src.n8n.executor.n8n_client.get_execution",
            return_value={"status": "success", "finished": True},
        ):
            from src.n8n.executor import execute_intent

            self._run(execute_intent("summarize my gmail", {}))
            self.assertEqual(order, ["sync", "trigger"])

    def test_llm_fill_invoked(self) -> None:
        skeleton = {
            "id": "gmail_read_summary",
            "parameter_schema": {"max_messages": {"default": 5}},
        }
        with patch(
            "src.n8n.executor.run_agent", return_value='{"max_messages": 3}'
        ) as mock_agent:
            from src.n8n.executor import _fill_with_llm

            result = _fill_with_llm("summarize 3 emails", skeleton, {})
            mock_agent.assert_called_once()
            self.assertEqual(result["max_messages"], 3)

    def test_poll_execution_success(self) -> None:
        from src.n8n import executor

        with patch(
            "src.n8n.executor.n8n_client.get_execution",
            return_value={"status": "success", "finished": True},
        ):
            result = self._run(executor._poll_execution("1"))
            self.assertEqual(result["status"], "success")

    def test_retry_once_on_failure(self) -> None:
        from src.n8n import executor

        with patch(
            "src.n8n.executor.n8n_client.trigger_workflow",
            return_value={"executionId": "1"},
        ), patch(
            "src.n8n.executor.n8n_client.get_execution",
            return_value={"status": "error", "error": "boom"},
        ):
            result = self._run(
                executor._retry_and_report("1", {}, {"error": "boom"}, "do it")
            )
            self.assertEqual(result["status"], "error")
            self.assertIn("message", result)


class CallbackTests(unittest.TestCase):
    def test_callback_logs_execution(self) -> None:
        import json
        import tempfile
        from pathlib import Path

        from fastapi.testclient import TestClient
        from src.app import app

        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "n8n_executions.json"
            with patch("src.api.n8n_callback._EXECUTION_LOG_PATH", log_path):
                client = TestClient(app)
                resp = client.post(
                    "/api/v1/webhook/n8n",
                    json={"executionId": "42", "status": "success", "data": {"r": 1}},
                )
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.json()["status"], "ok")
                entries = json.loads(log_path.read_text())
                self.assertEqual(entries[-1]["execution_id"], "42")
                self.assertIn("timestamp", entries[-1])

    def test_callback_invalid_json(self) -> None:
        from fastapi.testclient import TestClient
        from src.app import app

        client = TestClient(app)
        resp = client.post(
            "/api/v1/webhook/n8n",
            content="not json",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "error")


if __name__ == "__main__":
    unittest.main()
