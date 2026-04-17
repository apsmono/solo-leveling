"""
Notion integration client.

Provides read and write access to Notion databases and pages.
Uses the official Notion API via the notion-client SDK.

Environment variables required:
    NOTION_API_TOKEN   — internal integration token from notion.so/my-integrations

Usage:
    from src.integrations.notion.client import search, get_page, create_page
"""

import os
import logging
from typing import Any

from notion_client import Client  # type: ignore

logger = logging.getLogger(__name__)


def _client() -> Client:
    token = os.environ.get("NOTION_API_TOKEN")
    if not token:
        raise EnvironmentError(
            "NOTION_API_TOKEN is not set. "
            "Create an internal integration at notion.so/my-integrations and copy the token to .env."
        )
    return Client(auth=token)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """
    Search Notion for pages or databases matching `query`.
    Returns a list of simplified result dicts: {id, title, url, type}.
    """
    response = _client().search(query=query, page_size=limit)
    results = []
    for item in response.get("results", []):
        results.append({
            "id": item["id"],
            "title": _extract_title(item),
            "url": item.get("url", ""),
            "type": item["object"],  # "page" or "database"
        })
    logger.info("Notion search for '%s' returned %d results.", query, len(results))
    return results


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def get_page(page_id: str) -> dict[str, Any]:
    """Return the full Notion page object for `page_id`."""
    return _client().pages.retrieve(page_id=page_id)


def get_page_content(page_id: str) -> str:
    """
    Return the plain-text content of a Notion page by reading its blocks.
    Only paragraph, heading, and bulleted/numbered list blocks are included.
    """
    blocks = _client().blocks.children.list(block_id=page_id)
    lines = []
    for block in blocks.get("results", []):
        text = _extract_block_text(block)
        if text:
            lines.append(text)
    return "\n".join(lines)


def create_page(parent_id: str, title: str, content: str) -> dict[str, Any]:
    """
    Create a new Notion page under `parent_id` (a page or database ID).
    `content` is written as a single paragraph block.
    Returns the created page object.
    """
    new_page = _client().pages.create(
        parent={"page_id": parent_id},
        properties={
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        },
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                },
            }
        ],
    )
    logger.info("Created Notion page '%s' under parent %s.", title, parent_id)
    return new_page


# ---------------------------------------------------------------------------
# Databases
# ---------------------------------------------------------------------------

def query_database(database_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """
    Return rows from a Notion database as simplified dicts: {id, title, url}.
    """
    response = _client().databases.query(database_id=database_id, page_size=limit)
    rows = []
    for item in response.get("results", []):
        rows.append({
            "id": item["id"],
            "title": _extract_title(item),
            "url": item.get("url", ""),
        })
    return rows


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_title(item: dict) -> str:
    """Extract the title string from a Notion page or database object."""
    try:
        if item["object"] == "database":
            parts = item.get("title", [])
        else:
            title_prop = item.get("properties", {}).get("title") or item.get("properties", {}).get("Name", {})
            parts = title_prop.get("title", []) if title_prop else []
        return "".join(p.get("plain_text", "") for p in parts)
    except (KeyError, TypeError):
        return "(untitled)"


def _extract_block_text(block: dict) -> str:
    """Extract plain text from a Notion block."""
    block_type = block.get("type", "")
    block_data = block.get(block_type, {})
    rich_text = block_data.get("rich_text", [])
    return "".join(t.get("plain_text", "") for t in rich_text)
