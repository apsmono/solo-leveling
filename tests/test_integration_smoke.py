from __future__ import annotations

import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch, mock_open, Mock

from dotenv import load_dotenv

# Load .env file at module level so environment variables are available for all tests
load_dotenv()

from src.agents import dispatcher
from src.core import router, workflows
from src.integrations.gmail import client as gmail
from src.integrations.gdrive import client as gdrive
from src.integrations.notion import client as notion


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


def _drive_credentials_path() -> str | None:
    return os.environ.get("GOOGLE_DRIVE_CREDENTIALS_PATH") or os.environ.get("GOOGLE_CREDENTIALS_PATH")


def _gmail_credentials_path() -> str | None:
    return os.environ.get("GMAIL_CREDENTIALS_PATH") or os.environ.get("GOOGLE_CREDENTIALS_PATH")


def _is_headless_environment() -> bool:
    return any(
        os.environ.get(key, "").strip().lower() in {"1", "true", "yes"}
        for key in ("CI", "GITHUB_ACTIONS", "BUILD_BUILDID")
    )


class RouterSmokeTests(unittest.TestCase):
    def test_route_status_smoke(self) -> None:
        result = router.route_command("status")
        self.assertEqual(result, "Brain is online and listening.")

    def test_route_health_smoke(self) -> None:
        with patch.dict(
            os.environ,
            {
                "NOTION_API_TOKEN": "x",
                "GOOGLE_DRIVE_CREDENTIALS_PATH": "/tmp/drive-creds.json",
                "GMAIL_CREDENTIALS_PATH": "/tmp/gmail-creds.json",
                "GEMINI_API_KEY": "x",
            },
            clear=True,
        ):
            result = router.route_command("health")

        self.assertIn("Gemini", result)
        self.assertIn("All integrations configured.", result)

    def test_route_health_smoke_missing_gemini(self) -> None:
        with patch.dict(
            os.environ,
            {
                "NOTION_API_TOKEN": "x",
            },
            clear=True,
        ):
            result = router.route_command("health")

        self.assertIn("Gemini", result)
        self.assertIn("GEMINI_API_KEY", result)

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
        with patch("src.core.router.gmail.inbox_summary", return_value="You have 1 unread email(s):"), \
             patch.dict(os.environ, {"GMAIL_ENABLED": "true"}):
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

    def test_ai_dispatch_guardrail_without_gemini_key(self) -> None:
        with patch("src.agents.dispatcher.PROVIDER", "gemini"):
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(EnvironmentError, "GEMINI_API_KEY is not set"):
                    dispatcher.run_agent("Say OK")


class InlineCredentialSupportTests(unittest.TestCase):
    def test_gdrive_inline_credentials_json(self) -> None:
        with patch.dict(
            os.environ,
            {"GOOGLE_DRIVE_CREDENTIALS_JSON": '{"type":"service_account","client_email":"x","token_uri":"https://oauth2.googleapis.com/token","private_key":"-----BEGIN PRIVATE KEY-----\\nabc\\n-----END PRIVATE KEY-----\\n"}'},
            clear=True,
        ), patch("src.integrations.gdrive.client.service_account.Credentials.from_service_account_info", return_value="creds") as from_info, \
             patch("src.integrations.gdrive.client.service_account.Credentials.from_service_account_file") as from_file, \
             patch("src.integrations.gdrive.client.build", return_value="service") as build_mock:
            service = gdrive._service()

        self.assertEqual(service, "service")
        from_info.assert_called_once()
        from_file.assert_not_called()
        build_mock.assert_called_once_with("drive", "v3", credentials="creds")

    def test_gmail_inline_credentials_json(self) -> None:
        fake_creds = Mock()
        fake_creds.to_json.return_value = "{}"

        with patch.dict(
            os.environ,
            {
                "GMAIL_CREDENTIALS_JSON": '{"installed":{"client_id":"x","project_id":"p","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","client_secret":"s","redirect_uris":["http://localhost"]}}'
            },
            clear=True,
        ), patch("src.integrations.gmail.client._TOKEN_PATH", "/tmp/test-gmail-token.json"), \
             patch("src.integrations.gmail.client.os.path.exists", return_value=False), \
             patch("src.integrations.gmail.client.InstalledAppFlow.from_client_config") as from_config, \
             patch("src.integrations.gmail.client.InstalledAppFlow.from_client_secrets_file") as from_file, \
             patch("src.integrations.gmail.client.build", return_value="gmail_service") as build_mock, \
             patch("builtins.open", mock_open()):
            flow = Mock()
            flow.run_local_server.return_value = fake_creds
            from_config.return_value = flow

            service = gmail._service()

        self.assertEqual(service, "gmail_service")
        from_config.assert_called_once()
        from_file.assert_not_called()
        build_mock.assert_called_once_with("gmail", "v1", credentials=fake_creds)


@unittest.skipUnless(
    os.environ.get("ENABLE_LIVE_SMOKE_TESTS", "").lower() in ("1", "true", "yes"),
    "Set ENABLE_LIVE_SMOKE_TESTS=1 to run live integration smoke tests.",
)
class LiveIntegrationSmokeTests(unittest.TestCase):
    def test_live_notion_search_smoke(self) -> None:
        if not os.environ.get("NOTION_API_TOKEN"):
            self.skipTest("Set NOTION_API_TOKEN to run the live Notion smoke test.")

        results = notion.search("brain", limit=1)
        self.assertIsInstance(results, list)

    def test_live_drive_list_smoke(self) -> None:
        creds_kind = _credential_file_kind(_drive_credentials_path())
        if creds_kind != "service_account":
            self.skipTest(
                "Set GOOGLE_DRIVE_CREDENTIALS_PATH to a service-account JSON to run the live Drive smoke test."
            )

        files = gdrive.list_files(limit=1)
        self.assertIsInstance(files, list)

    def test_live_gmail_list_smoke(self) -> None:
        token_path = Path(os.environ.get("GMAIL_TOKEN_PATH", ".gmail_token.json"))
        creds_kind = _credential_file_kind(_gmail_credentials_path())
        allow_interactive = os.environ.get("ALLOW_INTERACTIVE_OAUTH_SMOKE", "").strip().lower() in {"1", "true", "yes"}

        if token_path.exists():
            messages = gmail.list_unread(limit=1)
            self.assertIsInstance(messages, list)
            return

        if creds_kind != "oauth_client":
            self.skipTest(
                "Set GMAIL_CREDENTIALS_PATH to OAuth client credentials or provide GMAIL_TOKEN_PATH to run the live Gmail smoke test."
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
