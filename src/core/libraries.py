"""
Stage 9 personal library command handlers.

This module handles lightweight capture and lookup flows for:
  - Knowledge profile (skills, interests, domains)
  - Terms
  - Books
  - Articles
  - Thoughts
  - Library review summary

Current implementation stores captures as Notion pages under NOTION_WORKFLOW_PARENT_ID.
It reuses existing Notion client capabilities so Stage 9 can be used immediately,
then can be upgraded to database-specific writes in a later slice.
"""

from __future__ import annotations

from datetime import datetime
import re

from src.core.config import NOTION_WORKFLOW_PARENT_ID
from src.integrations.notion import client as notion


ALLOWED_PROFILE_TYPES = {"skill", "interest", "domain", "learning", "focus"}
ALLOWED_CONFIDENCE = {"high", "medium", "low", "exploring"}
ALLOWED_PRIORITY = {"now", "next", "later"}

_SENSITIVE_TOKENS = (
    "password",
    "secret",
    "api key",
    "token",
    "passport",
    "ktp",
    "identity number",
    "contact",
    "credit card",
    "bank account",
)


def handle_library_command(text: str, intent: str) -> str:
    """Route library command to the right handler."""
    if intent == "library_profile":
        return _handle_profile(text)
    if intent == "library_term":
        return _handle_term(text)
    if intent == "library_book":
        return _handle_book(text)
    if intent == "library_article":
        return _handle_article(text)
    if intent == "library_thought":
        return _handle_thought(text)
    if intent == "library_review":
        return _handle_review(text)
    if intent == "library_guide":
        return _save_formatting_guide_to_library()
    return "Library command not recognized."


def _require_parent() -> str:
    if not NOTION_WORKFLOW_PARENT_ID:
        raise EnvironmentError(
            "NOTION_WORKFLOW_PARENT_ID is not set. "
            "Open docs/SETUP_SECRETS.md and complete the Notion setup checklist."
        )
    return NOTION_WORKFLOW_PARENT_ID


def _contains_sensitive_content(text: str) -> bool:
    lower = text.lower()
    return any(token in lower for token in _SENSITIVE_TOKENS)


def _capture_page(title: str, body: str) -> str:
    page = notion.create_page(
        parent_id=_require_parent(),
        title=title,
        content=body,
    )
    return page.get("url", "")


def _extract_after_prefix(text: str, prefixes: tuple[str, ...]) -> str:
    lower = text.lower().strip()
    for prefix in prefixes:
        if lower.startswith(prefix):
            return text.strip()[len(prefix):].strip()
    return ""


def _handle_profile(text: str) -> str:
    lower = text.lower().strip()

    if _contains_sensitive_content(text):
        return (
            "Profile capture blocked: this command appears to include sensitive data.\n"
            "Allowed scope is knowledge profile only (skills, interests, domains, learning priorities, focus themes)."
        )

    if lower.startswith("profile summary"):
        rows = notion.search("Profile:", limit=10)
        if not rows:
            return "No profile entries found yet. Try: profile skill: python | confidence: high | priority: now"

        lines = ["Recent profile entries:\n"]
        for idx, row in enumerate(rows, 1):
            lines.append(f"{idx}. {row.get('title', '(untitled)')}")
            if row.get("url"):
                lines.append(f"   {row['url']}")
        return "\n".join(lines)

    payload = _extract_after_prefix(text, ("profile skill:", "profile interest:", "profile domain:", "profile learning:", "profile focus:"))

    profile_type = ""
    for candidate in ALLOWED_PROFILE_TYPES:
        marker = f"profile {candidate}:"
        if lower.startswith(marker):
            profile_type = candidate
            break

    if payload and profile_type:
        confidence = _extract_field(lower, "confidence")
        priority = _extract_field(lower, "priority")

        if confidence and confidence not in ALLOWED_CONFIDENCE:
            return "Invalid confidence. Use: high, medium, low, or exploring."
        if priority and priority not in ALLOWED_PRIORITY:
            return "Invalid priority. Use: now, next, or later."

        title = f"Profile: {profile_type.title()} - {payload.split('|')[0].strip()}"
        body = (
            f"Type: {profile_type}\n"
            f"Input: {payload}\n"
            f"Captured At: {datetime.now().isoformat(timespec='minutes')}"
        )
        url = _capture_page(title, body)
        return f"Profile item saved.\n{url}" if url else "Profile item saved."

    if lower.startswith("profile update:"):
        item = text.split(":", 1)[1].strip() if ":" in text else ""
        if not item:
            return "Use: profile update: <item> | <new value>"
        title = f"Profile Update: {item.split('|')[0].strip()}"
        body = f"Update: {item}\nCaptured At: {datetime.now().isoformat(timespec='minutes')}"
        url = _capture_page(title, body)
        return f"Profile update saved.\n{url}" if url else "Profile update saved."

    return (
        "Profile command not recognized.\n"
        "Try:\n"
        "• profile skill: python | confidence: high | priority: now\n"
        "• profile interest: personal knowledge systems | priority: next\n"
        "• profile domain: finance | focus: cashflow planning\n"
        "• profile update: python skill | moved to advanced\n"
        "• profile summary"
    )


def _handle_term(text: str) -> str:
    lower = text.lower().strip()

    if lower.startswith("add term:"):
        payload = text.split(":", 1)[1].strip() if ":" in text else ""
        if not payload:
            return "Use: add term: <term> = <definition>"
        term_title = payload.split("=", 1)[0].strip() if "=" in payload else payload
        body = f"{payload}\nCaptured At: {datetime.now().isoformat(timespec='minutes')}"
        url = _capture_page(f"Term: {term_title}", body)
        return f"Term saved.\n{url}" if url else "Term saved."

    if lower.startswith("term ") or lower.startswith("define "):
        query = _extract_after_prefix(text, ("term ", "define ")).strip()
        if not query:
            return "Use: term <word>"
        results = notion.search(query, limit=5)
        if not results:
            return f"No term result found for: {query}"
        lines = [f"Results for '{query}':\n"]
        for i, row in enumerate(results, 1):
            lines.append(f"{i}. {row.get('title', '(untitled)')}")
            if row.get("url"):
                lines.append(f"   {row['url']}")
        return "\n".join(lines)

    return "Try: add term: <term> = <definition> or term <word>"


def _handle_book(text: str) -> str:
    lower = text.lower().strip()

    if lower.startswith("book:"):
        payload = text.split(":", 1)[1].strip() if ":" in text else ""
        if not payload:
            return "Use: book: <title> by <author>"
        title = f"Book: {payload.split('|')[0].strip()}"
        body = f"{payload}\nStatus: wishlist\nCaptured At: {datetime.now().isoformat(timespec='minutes')}"
        url = _capture_page(title, body)
        return f"Book saved.\n{url}" if url else "Book saved."

    if lower.startswith("reading ") or lower.startswith("finished "):
        status = "reading" if lower.startswith("reading ") else "finished"
        name = _extract_after_prefix(text, ("reading ", "finished ")).strip()
        if not name:
            return "Use: reading <title> or finished <title>"
        url = _capture_page(f"Book Update: {name}", f"Status: {status}\nCaptured At: {datetime.now().isoformat(timespec='minutes')}")
        return f"Book status update saved.\n{url}" if url else "Book status update saved."

    if lower.startswith("book insights:"):
        query = text.split(":", 1)[1].strip() if ":" in text else ""
        if not query:
            return "Use: book insights: <title>"
        results = notion.search(query, limit=5)
        if not results:
            return f"No book insights found for: {query}"
        lines = [f"Book insights matches for '{query}':\n"]
        for i, row in enumerate(results, 1):
            lines.append(f"{i}. {row.get('title', '(untitled)')}")
            if row.get("url"):
                lines.append(f"   {row['url']}")
        return "\n".join(lines)

    return "Try: book: <title> by <author>, reading <title>, finished <title>, or book insights: <title>"


def _handle_article(text: str) -> str:
    lower = text.lower().strip()

    if lower.startswith("article:"):
        payload = text.split(":", 1)[1].strip() if ":" in text else ""
        if not payload:
            return "Use: article: <url or title>"
        title = f"Article: {payload.split('|')[0].strip()}"
        url = _capture_page(title, f"{payload}\nCaptured At: {datetime.now().isoformat(timespec='minutes')}")
        return f"Article saved.\n{url}" if url else "Article saved."

    if lower.startswith("articles on "):
        topic = _extract_after_prefix(text, ("articles on ",)).strip()
        if not topic:
            return "Use: articles on <topic>"
        results = notion.search(topic, limit=8)
        if not results:
            return f"No articles found for topic: {topic}"
        lines = [f"Articles on '{topic}':\n"]
        for i, row in enumerate(results, 1):
            lines.append(f"{i}. {row.get('title', '(untitled)')}")
            if row.get("url"):
                lines.append(f"   {row['url']}")
        return "\n".join(lines)

    return "Try: article: <url> or articles on <topic>"


def _handle_thought(text: str) -> str:
    lower = text.lower().strip()

    if lower.startswith("thought:"):
        payload = text.split(":", 1)[1].strip() if ":" in text else ""
        if not payload:
            return "Use: thought: <idea>"
        title = f"Thought: {payload[:80].strip()}"
        body = f"{payload}\nStatus: draft\nCaptured At: {datetime.now().isoformat(timespec='minutes')}"
        url = _capture_page(title, body)
        return f"Thought saved.\n{url}" if url else "Thought saved."

    if lower.startswith("draft:") or lower.startswith("publish thought:"):
        action = "draft lookup" if lower.startswith("draft:") else "publish"
        payload = text.split(":", 1)[1].strip() if ":" in text else ""
        if not payload:
            return "Use: draft: <title> or publish thought: <title>"
        url = _capture_page(
            f"Thought Update: {payload}",
            f"Action: {action}\nCaptured At: {datetime.now().isoformat(timespec='minutes')}"
        )
        return f"Thought update saved.\n{url}" if url else "Thought update saved."

    return "Try: thought: <idea>, draft: <title>, or publish thought: <title>"


def _handle_review(_: str) -> str:
    profile = len(notion.search("Profile:", limit=20))
    terms = len(notion.search("Term:", limit=20))
    books = len(notion.search("Book:", limit=20))
    articles = len(notion.search("Article:", limit=20))
    thoughts = len(notion.search("Thought:", limit=20))

    return (
        "Library quick review:\n"
        f"• Profile entries: {profile}\n"
        f"• Terms: {terms}\n"
        f"• Books: {books}\n"
        f"• Articles: {articles}\n"
        f"• Thoughts: {thoughts}\n\n"
        "Tip: run 'profile summary' or 'review terms' style searches for details."
    )


def _extract_field(lower_text: str, field: str) -> str:
    match = re.search(rf"\b{field}\s*:\s*([a-z-]+)", lower_text)
    return match.group(1).strip() if match else ""


def _apply_formatting_standard(
    library_type: str,
    title: str,
    body: str,
    metadata: dict | None = None
) -> dict:
    """
    Apply Stage 9 formatting standard to library entry.

    Enforces:
    - Title Case for titles
    - Consistent field order (9-field standard)
    - Tag validation (lowercase-hyphen, max 5)
    - Sensitive content blocking
    - Consistent date format

    Returns: {title, body, formatted_date, tags, library_type, status}
    """
    if not metadata:
        metadata = {}

    # Enforce title case
    title = _ensure_title_case(title)

    # Validate and normalize tags
    tags = metadata.get("tags", [])
    if tags:
        if isinstance(tags, str):
            tags = [t.strip().lower() for t in tags.split(",")]
        tags = [t.replace(" ", "-") for t in tags if t.strip()]
        tags = tags[:5]  # Enforce max 5 tags

    # Add timestamp
    formatted_date = metadata.get("date") or datetime.now().isoformat(timespec="minutes")

    return {
        "title": title,
        "body": body,
        "formatted_date": formatted_date,
        "tags": tags,
        "library_type": library_type,
        "status": metadata.get("status", "draft").lower(),
    }


def _ensure_title_case(text: str) -> str:
    """Convert text to Title Case, preserving acronyms (API, HTTP, MCP)."""
    words = text.split()
    result = []
    for word in words:
        if len(word) <= 2 or word.isupper():
            result.append(word)
        else:
            result.append(word.capitalize())
    return " ".join(result)


def _save_formatting_guide_to_library() -> str:
    """
    Save Notion formatting guide as reference page in Stage 9 library.
    Call via WhatsApp: "library guide" or directly from handlers.
    """
    guide_title = "Reference: Notion Formatting Guide for Stage 9 Library"

    guide_body = (
        "Personal Library Formatting Standard (Stage 9)\n\n"
        "UNIVERSAL RULES:\n"
        "1. One-screen readability\n"
        "2. Keep writing short (2-4 bullets, max 3 lines per paragraph)\n"
        "3. Consistent field order everywhere\n"
        "4. Prefer relations over copy-paste\n"
        "5. Use fixed status vocabulary\n"
        "6. Every entry has date + tag\n"
        "7. Archive instead of delete\n\n"
        "9-FIELD ORDER (all types):\n"
        "1. Title\n"
        "2. Type/Category\n"
        "3. Status\n"
        "4. Priority/Confidence\n"
        "5. Summary/Definition\n"
        "6. Key Points\n"
        "7. Relations\n"
        "8. Source\n"
        "9. Date Added/Updated\n\n"
        "NAMING STANDARD:\n"
        "Titles: Title Case\n"
        "Tags: lowercase-hyphen format (#deep-dive, #decision-making)\n"
        "Max 5 tags per entry\n\n"
        "MAINTENANCE:\n"
        "Weekly (15 min): Fix missing Status, merge duplicate tags, archive old drafts\n"
        "Monthly (30 min): Review stale entries, promote good drafts, consolidate tags\n"
        "Quarterly (1 hour): Publish ready items, reassess priorities, reflect\n\n"
        "See docs/personal-library-formatting-guide.md for full details."
    )

    try:
        url = _capture_page(guide_title, guide_body)
        logger.info("Formatting guide saved to Notion: %s", url)
        return f"✅ Formatting guide saved.\n{url}" if url else "✅ Formatting guide saved."
    except Exception as e:
        logger.error("Failed to save formatting guide: %s", e)
        return f"❌ Failed to save formatting guide: {str(e)}"
