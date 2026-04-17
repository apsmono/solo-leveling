"""
Stage 8 workflow composition layer.

This module handles multi-step commands that combine multiple integrations.
Current workflows implemented:
  - Summarise unread inbox and save the summary as a Notion page.
  - Summarise unread inbox and save the summary as a Google Doc.
  - Query a Notion database and export results as a Google Doc.
"""

from __future__ import annotations

from datetime import datetime

from src.core.config import NOTION_WORKFLOW_PARENT_ID
from src.integrations.gmail import client as gmail
from src.integrations.notion import client as notion
from src.integrations.gdrive import client as drive


def handle_workflow_command(text: str) -> str:
    """Route compound command text to the right workflow."""
    lower = text.strip().lower()

    if _is_inbox_to_notion_workflow(lower):
        return _workflow_inbox_summary_to_notion()

    if _is_inbox_to_drive_workflow(lower):
        return _workflow_inbox_summary_to_drive()

    if _is_notion_to_drive_workflow(lower):
        return _workflow_notion_query_to_drive(text)

    return (
        "Workflow command not recognised.\n\n"
        "Try:\n"
        "• summarise my inbox and save to notion\n"
        "• summarize inbox and save to drive\n"
        "• query notion <query> and export to drive"
    )


def _is_inbox_to_notion_workflow(lower: str) -> bool:
    has_inbox = any(token in lower for token in ("inbox", "gmail", "email"))
    has_summary = any(token in lower for token in ("summarise", "summarize", "summary"))
    has_notion_save = "save to notion" in lower or ("save" in lower and "notion" in lower)
    return has_inbox and has_summary and has_notion_save


def _is_inbox_to_drive_workflow(lower: str) -> bool:
    has_inbox = any(token in lower for token in ("inbox", "gmail", "email"))
    has_summary = any(token in lower for token in ("summarise", "summarize", "summary"))
    has_drive_save = "save to drive" in lower or ("save" in lower and "drive" in lower)
    return has_inbox and has_summary and has_drive_save


def _is_notion_to_drive_workflow(lower: str) -> bool:
    has_query = "query notion" in lower or "notion query" in lower
    has_export = "export to drive" in lower or ("export" in lower and "drive" in lower)
    return has_query and has_export


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


def _workflow_inbox_summary_to_drive() -> str:
    """Summarise unread inbox and save to Google Drive as a new Doc."""
    summary = gmail.inbox_summary(limit=5)
    title = f"Inbox Summary {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    doc = drive.create_doc(name=title, content=summary)

    url = doc.get("webViewLink", "")
    response = [
        "Workflow completed.",
        "Step 1: Read and summarised unread Gmail inbox.",
        "Step 2: Saved summary to Google Drive.",
    ]
    if url:
        response.append(f"Google Doc: {url}")
    return "\n".join(response)


def _workflow_notion_query_to_drive(text: str) -> str:
    """Query Notion database and export results to Google Drive Doc."""
    # Extract query term from text like "query notion <query> and export to drive"
    lower = text.lower()
    query_start = lower.find("notion") + 6
    query_end = lower.find(" and export", query_start)
    if query_start >= 6 and query_end > query_start:
        query = text[query_start:query_end].strip()
    else:
        query = "tasks"  # Default fallback query

    results = notion.search(query=query, limit=10)

    if not results:
        return f"No Notion results found for query: {query}"

    # Format results as plain text
    lines = [f"Notion Search Results: {query}\n"]
    for i, result in enumerate(results, 1):
        lines.append(f"{i}. {result['title']}")
        lines.append(f"   Type: {result['type']}")
        if result.get("url"):
            lines.append(f"   URL: {result['url']}")
        lines.append("")

    content = "\n".join(lines)
    title = f"Notion Query {query} {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    doc = drive.create_doc(name=title, content=content)

    url = doc.get("webViewLink", "")
    response = [
        "Workflow completed.",
        f"Step 1: Queried Notion for '{query}'.",
        f"Step 2: Found {len(results)} result(s).",
        "Step 3: Exported results to Google Drive.",
    ]
    if url:
        response.append(f"Google Doc: {url}")
    return "\n".join(response)
