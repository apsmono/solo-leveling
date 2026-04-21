from __future__ import annotations

import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from src.agents import dispatcher
from src.core import router, workflows
from src.integrations.gmail import client as gmail
from src.integrations.gdrive import client as gdrive
from src.integrations.notion import client as notion
from src.integrations.whatsapp import handler as whatsapp_handler


def _credential_file_kind(path_value: str | None) -> str:
    if not path_value:
        return "missing"

    path = Path(path_value)
    if not path.exists():
        return "missing"

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "unknown"

    if payload.get("type") == "service_account":
        return "service_account"
    if "installed" in payload or "web" in payload:
        return "oauth_client"
    return "unknown"


def _is_headless_environment() -> bool:
    return any(
        os.environ.get(key, "").strip().lower() in {"1", "true", "yes"}
        for key in ("CI", "GITHUB_ACTIONS", "BUILD_BUILDID")
    )


class RouterSmokeTests(unittest.TestCase):
    def test_route_status_smoke(self) -> None:
        result = router.route_command("status")
        self.assertEqual(result, "Brain is online and listening.")

    def test_route_notion_smoke_with_mocked_client(self) -> None:
        with patch("src.core.router.notion.search", return_value=[{"title": "Roadmap", "type": "page", "url": "https://notion.test/page"}]):
            result = router.route_command("notion roadmap")

        self.assertIn("Notion results for 'roadmap':", result)
        self.assertIn("Roadmap", result)

    def test_route_notion_smoke_empty_results(self) -> None:
        with patch("src.core.router.notion.search", return_value=[]):
            result = router.route_command("notion roadmap")

        self.assertEqual(result, "No Notion results found for: roadmap")

    def test_route_drive_smoke_with_mocked_client(self) -> None:
        with patch("src.core.router.gdrive.list_files", return_value=[{"name": "Weekly Review", "webViewLink": "https://drive.test/doc"}]):
            result = router.route_command("drive")

        self.assertIn("Recent Google Drive files:", result)
        self.assertIn("Weekly Review", result)

    def test_route_drive_smoke_empty_results(self) -> None:
        with patch("src.core.router.gdrive.list_files", return_value=[]):
            result = router.route_command("drive")

        self.assertEqual(result, "No files found in Google Drive.")

    def test_route_gmail_smoke_with_mocked_client(self) -> None:
        with patch("src.core.router.gmail.inbox_summary", return_value="You have 1 unread email(s):"):
            result = router.route_command("email")

        self.assertEqual(result, "You have 1 unread email(s):")

    def test_route_ai_smoke_with_mocked_dispatch(self) -> None:
        with patch("src.core.router.run_agent", return_value="Priorities: focus, write, review"):
            result = router.route_command("ask summarize my priorities")

        self.assertEqual(result, "Priorities: focus, write, review")

    def test_workflow_guardrail_without_notion_parent(self) -> None:
        with patch("src.core.workflows.NOTION_WORKFLOW_PARENT_ID", ""):
            result = workflows.handle_workflow_command("summarise my inbox and save to notion")

        self.assertIn("Workflow blocked: NOTION_WORKFLOW_PARENT_ID is not set.", result)

    def test_ai_dispatch_guardrail_without_openai_key(self) -> None:
        with patch("src.agents.dispatcher.PROVIDER", "openai"):
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(EnvironmentError, "OPENAI_API_KEY is not set"):
                    dispatcher.run_agent("Say OK")

    def test_whatsapp_payload_extract_smoke(self) -> None:
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "628123456789",
                                        "text": {"body": "status"},
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        sender, text = whatsapp_handler._extract_message(payload)
        self.assertEqual(sender, "628123456789")
        self.assertEqual(text, "status")

    def test_whatsapp_payload_extract_smoke_malformed(self) -> None:
        sender, text = whatsapp_handler._extract_message({"entry": []})
        self.assertEqual(sender, "")
        self.assertEqual(text, "")


class LiveIntegrationSmokeTests(unittest.TestCase):
    def test_live_notion_search_smoke(self) -> None:
        if not os.environ.get("NOTION_API_TOKEN"):
            self.skipTest("Set NOTION_API_TOKEN to run the live Notion smoke test.")

        results = notion.search("brain", limit=1)
        self.assertIsInstance(results, list)

    def test_live_drive_list_smoke(self) -> None:
        creds_kind = _credential_file_kind(os.environ.get("GOOGLE_CREDENTIALS_PATH"))
        if creds_kind != "service_account":
            self.skipTest(
                "Set GOOGLE_CREDENTIALS_PATH to a service-account JSON to run the live Drive smoke test."
            )

        files = gdrive.list_files(limit=1)
        self.assertIsInstance(files, list)

    def test_live_gmail_list_smoke(self) -> None:
        token_path = Path(os.environ.get("GMAIL_TOKEN_PATH", ".gmail_token.json"))
        creds_kind = _credential_file_kind(os.environ.get("GOOGLE_CREDENTIALS_PATH"))
        allow_interactive = os.environ.get("ALLOW_INTERACTIVE_OAUTH_SMOKE", "").strip().lower() in {"1", "true", "yes"}

        if token_path.exists():
            messages = gmail.list_unread(limit=1)
            self.assertIsInstance(messages, list)
            return

        if creds_kind != "oauth_client":
            self.skipTest(
                "Set GOOGLE_CREDENTIALS_PATH to OAuth client credentials or provide GMAIL_TOKEN_PATH to run the live Gmail smoke test."
            )

        if _is_headless_environment() and not allow_interactive:
            self.skipTest(
                "Headless environment detected. Set GMAIL_TOKEN_PATH with an existing token or ALLOW_INTERACTIVE_OAUTH_SMOKE=true to permit OAuth browser flow."
            )

        if not allow_interactive:
            self.skipTest(
                "Interactive OAuth is disabled by default. Set ALLOW_INTERACTIVE_OAUTH_SMOKE=true to run this live Gmail smoke test with OAuth browser consent."
            )

        messages = gmail.list_unread(limit=1)
        self.assertIsInstance(messages, list)
