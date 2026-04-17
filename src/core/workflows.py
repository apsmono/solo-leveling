"""
Stage 8 workflow composition layer.

This module handles multi-step commands that combine multiple integrations.
Current workflow implemented:
  - Summarise unread inbox and save the summary as a Notion page.
"""

from __future__ import annotations

from datetime import datetime

from src.core.config import NOTION_WORKFLOW_PARENT_ID
from src.integrations.gmail import client as gmail
from src.integrations.notion import client as notion


def handle_workflow_command(text: str) -> str:
    """Route compound command text to the right workflow."""
    lower = text.strip().lower()

    if _is_inbox_to_notion_workflow(lower):
        return _workflow_inbox_summary_to_notion()

    return (
        "Workflow command not recognised.\n\n"
        "Try:\n"
        "• summarise my inbox and save to notion\n"
        "• summarize inbox and save to notion"
    )


def _is_inbox_to_notion_workflow(lower: str) -> bool:
    has_inbox = any(token in lower for token in ("inbox", "gmail", "email"))
    has_summary = any(token in lower for token in ("summarise", "summarize", "summary"))
    has_notion_save = "save to notion" in lower or ("save" in lower and "notion" in lower)
    return has_inbox and has_summary and has_notion_save


def _workflow_inbox_summary_to_notion() -> str:
    if not NOTION_WORKFLOW_PARENT_ID:
        return (
            "Workflow blocked: NOTION_WORKFLOW_PARENT_ID is not set.\n"
            "Open docs/SETUP_SECRETS.md and complete the Notion setup checklist."
        )

    summary = gmail.inbox_summary(limit=5)
    title = f"Inbox Summary {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    page = notion.create_page(
        parent_id=NOTION_WORKFLOW_PARENT_ID,
        title=title,
        content=summary,
    )

    url = page.get("url", "")
    response = [
        "Workflow completed.",
        "Step 1: Read and summarised unread Gmail inbox.",
        "Step 2: Saved summary into Notion.",
    ]
    if url:
        response.append(f"Notion page: {url}")
    return "\n".join(response)
