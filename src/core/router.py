"""
Command router — brain core.

Receives a text command string from the WhatsApp handler (or any other interface),
parses intent, dispatches to the correct handler, and returns a reply string.

Adding new commands:
    1. Add a new intent key and keywords to INTENT_MAP.
    2. Add a matching handler function below.
    3. Wire it into _dispatch().
"""

import logging

from src.core.scheduler import handle_reminder_command
from src.core.libraries import handle_library_command
from src.core.workflows import handle_workflow_command
from src.integrations.notion import client as notion
from src.integrations.gdrive import client as gdrive
from src.integrations.gmail import client as gmail
from src.agents.dispatcher import run_agent

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Intent map
# ---------------------------------------------------------------------------
# Keys are intent names; values are lists of trigger keywords (lowercase).
INTENT_MAP: dict[str, list[str]] = {
    "help": ["help", "commands", "what can you do"],
    "status": ["status", "how are you", "ping"],
    "library_profile": ["profile skill", "profile interest", "profile domain", "profile update", "profile summary"],
    "library_term": ["add term:", "term ", "define ", "review terms"],
    "library_book": ["book:", "reading ", "finished ", "book insights:"],
    "library_article": ["article:", "articles on "],
    "library_thought": ["thought:", "draft:", "publish thought:"],
    "library_review": ["my library", "library status", "review books", "review terms"],
    "workflow": ["workflow", "save to notion", "and save"],
    "notion_search": ["notion", "read notion", "show notion", "find notion"],
    "gdrive_list": ["drive", "gdrive", "google drive", "list drive", "list files"],
    "gmail_summary": ["email", "gmail", "inbox", "unread", "emails"],
    "reminder": ["remind", "reminder", "notify me"],
    "ask_ai": ["ask", "ai ", "think about", "summarise", "summarize", "analyse", "analyze", "write", "draft"],
}


def route_command(text: str) -> str:
    """Parse intent from text and dispatch to the correct handler."""
    intent = _detect_intent(text)
    logger.info("Intent detected: %s", intent)
    return _dispatch(intent, text)


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------

def _detect_intent(text: str) -> str:
    lower = text.strip().lower()

    # Stage 8 compound workflow detection should run before keyword map because
    # terms like "notion", "inbox", "drive" also match single-step intents.
    # Detect inbox-to-notion, inbox-to-drive, notion-to-drive workflows
    if any(token in lower for token in ("inbox", "gmail", "email")) and any(token in lower for token in ("summarise", "summarize", "summary")) and any(token in lower for token in ("save to", "save")):
        return "workflow"

    if ("query notion" in lower or "notion query" in lower) and ("export to drive" in lower or ("export" in lower and "drive" in lower)):
        return "workflow"

    for intent, keywords in INTENT_MAP.items():
        if any(kw in lower for kw in keywords):
            return intent
    return "unknown"


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def _dispatch(intent: str, original_text: str) -> str:
    handlers = {
        "help": _handle_help,
        "status": _handle_status,
        "library_profile": _handle_library,
        "library_term": _handle_library,
        "library_book": _handle_library,
        "library_article": _handle_library,
        "library_thought": _handle_library,
        "library_review": _handle_library,
        "workflow": _handle_workflow,
        "notion_search": _handle_notion_search,
        "gdrive_list": _handle_gdrive_list,
        "gmail_summary": _handle_gmail_summary,
        "reminder": _handle_reminder,
        "ask_ai": _handle_ask_ai,
        "unknown": _handle_unknown,
    }
    handler = handlers.get(intent, _handle_unknown)
    try:
        return handler(original_text)
    except EnvironmentError as e:
        logger.error("Configuration error in handler '%s': %s", intent, e)
        return f"Configuration error: {e}\nCheck your .env file."
    except Exception as e:
        logger.exception("Unexpected error in handler '%s'.", intent)
        return f"Something went wrong while handling your request. ({type(e).__name__})"


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def _handle_help(_: str) -> str:
    return (
        "Brain command center ready.\n\n"
        "Available commands:\n"
        "• status — check if the brain is running\n"
        "• profile skill: <name> | confidence: high | priority: now\n"
        "• profile interest: <topic> | priority: next\n"
        "• profile domain: <domain> | focus: <note>\n"
        "• profile update: <item> | <new value>\n"
        "• profile summary — list recent profile entries\n"
        "• add term: <term> = <definition>\n"
        "• term <word> — find saved term entries\n"
        "• book: <title> by <author>\n"
        "• article: <url>\n"
        "• thought: <idea>\n"
        "• my library — quick library counts\n"
        "• notion <query> — search Notion\n"
        "• drive — list recent Google Drive files\n"
        "• email — summarise unread Gmail inbox\n"
        "• summarise my inbox and save to notion\n"
        "• summarise my inbox and save to drive\n"
        "• query notion <query> and export to drive\n"
        "• ask <question> — ask the AI anything\n"
        "• remind me in 30 minutes to stretch\n"
        "• remind me tomorrow at 09:00 to review goals\n"
        "• reminders — list pending reminders\n"
        "• help — show this message"
    )


def _handle_status(_: str) -> str:
    return "Brain is online and listening."


def _handle_library(text: str) -> str:
    intent = _detect_intent(text)
    return handle_library_command(text=text, intent=intent)


def _handle_workflow(text: str) -> str:
    return handle_workflow_command(text)


def _handle_notion_search(text: str) -> str:
    # Extract the search query by stripping known trigger words
    query = text.lower()
    for kw in ("notion", "read notion", "show notion", "find notion"):
        query = query.replace(kw, "").strip()
    if not query:
        return "What would you like to search for in Notion? Try: notion <search term>"

    results = notion.search(query, limit=5)
    if not results:
        return f"No Notion results found for: {query}"

    lines = [f"Notion results for '{query}':\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']} ({r['type']})")
        if r.get("url"):
            lines.append(f"   {r['url']}")
    return "\n".join(lines)


def _handle_gdrive_list(text: str) -> str:
    files = gdrive.list_files(limit=8)
    if not files:
        return "No files found in Google Drive."

    lines = ["Recent Google Drive files:\n"]
    for i, f in enumerate(files, 1):
        lines.append(f"{i}. {f['name']}")
        if f.get("webViewLink"):
            lines.append(f"   {f['webViewLink']}")
    return "\n".join(lines)


def _handle_gmail_summary(text: str) -> str:
    return gmail.inbox_summary(limit=5)


def _handle_ask_ai(text: str) -> str:
    # Strip trigger words so only the actual question reaches the agent
    task = text
    for kw in ("ask ai", "ask", "think about", "summarise", "summarize", "analyse", "analyze", "write", "draft"):
        if task.lower().startswith(kw):
            task = task[len(kw):].strip()
            break
    if not task:
        return "What would you like me to think about? Try: ask <your question>"
    return run_agent(task=task)


def _handle_reminder(text: str) -> str:
    return handle_reminder_command(text)


def _handle_unknown(text: str) -> str:
    return (
        f'I didn\'t understand: "{text}"\n'
        "Send *help* to see available commands."
    )
