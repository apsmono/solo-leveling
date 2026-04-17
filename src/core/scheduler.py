"""
Notification scheduler for proactive reminders and digest jobs.

Stage 6 introduces a small persistent reminder system backed by a JSON file so
scheduled reminders survive process restarts. Jobs are executed by APScheduler
inside the same process as the webhook server.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from uuid import uuid4

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.core.config import (
    DAILY_GMAIL_DIGEST_ENABLED,
    DAILY_GMAIL_DIGEST_HOUR,
    DAILY_GMAIL_DIGEST_MINUTE,
    REMINDER_STORE_PATH,
    SCHEDULER_POLL_SECONDS,
    WHATSAPP_OWNER_NUMBER,
)
from src.integrations.gmail import client as gmail
from src.integrations.whatsapp.client import send_message

logger = logging.getLogger(__name__)

_RELATIVE_PATTERN = re.compile(
    r"^(?:remind(?: me)?|notify me)\s+in\s+(\d+)\s+(minutes?|hours?|days?)\s+(?:to\s+)?(.+)$",
    re.IGNORECASE,
)
_ABSOLUTE_PATTERN = re.compile(
    r"^(?:remind(?: me)?|notify me)\s+at\s+(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2})\s+(?:to\s+)?(.+)$",
    re.IGNORECASE,
)
_TOMORROW_PATTERN = re.compile(
    r"^(?:remind(?: me)?|notify me)\s+tomorrow\s+at\s+(\d{1,2}:\d{2})\s+(?:to\s+)?(.+)$",
    re.IGNORECASE,
)

_STORE_LOCK = Lock()
_scheduler: BackgroundScheduler | None = None


def handle_reminder_command(text: str) -> str:
    """Create or inspect reminders based on the inbound command text."""
    normalized = text.strip()
    lower = normalized.lower()

    if lower in {"reminders", "list reminders", "reminder list", "show reminders"}:
        return format_pending_reminders()

    run_at, message = _parse_reminder_text(normalized)
    if not run_at or not message:
        return (
            "Reminder format not understood.\n\n"
            "Try one of these:\n"
            "• remind me in 30 minutes to stretch\n"
            "• remind me in 2 hours to review goals\n"
            "• remind me tomorrow at 09:00 to check inbox\n"
            "• remind me at 2026-04-18 08:30 to plan the day\n"
            "• reminders"
        )

    reminder = create_reminder(message=message, run_at=run_at)
    return (
        "Reminder saved.\n"
        f"• When: {_format_timestamp(run_at)}\n"
        f"• What: {reminder['message']}"
    )


def create_reminder(message: str, run_at: datetime) -> dict[str, str]:
    reminder = {
        "id": uuid4().hex,
        "message": message.strip(),
        "run_at": run_at.isoformat(timespec="seconds"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "sent_at": "",
    }

    with _STORE_LOCK:
        reminders = _load_reminders()
        reminders.append(reminder)
        reminders.sort(key=lambda item: item["run_at"])
        _save_reminders(reminders)

    logger.info("Reminder scheduled for %s: %s", reminder["run_at"], reminder["message"])
    return reminder


def format_pending_reminders() -> str:
    reminders = [item for item in _load_reminders() if not item.get("sent_at")]
    if not reminders:
        return "No pending reminders."

    lines = ["Pending reminders:\n"]
    for index, reminder in enumerate(sorted(reminders, key=lambda item: item["run_at"]), start=1):
        lines.append(f"{index}. {_format_timestamp(datetime.fromisoformat(reminder['run_at']))}")
        lines.append(f"   {reminder['message']}")
    return "\n".join(lines)


def process_due_reminders() -> None:
    """Send any reminders whose due time has passed."""
    if not WHATSAPP_OWNER_NUMBER:
        logger.debug("Reminder processing skipped: WHATSAPP_OWNER_NUMBER is not set.")
        return

    now = datetime.now()
    due = [
        item for item in _load_reminders()
        if not item.get("sent_at") and datetime.fromisoformat(item["run_at"]) <= now
    ]
    if not due:
        return

    sent_ids: set[str] = set()
    for reminder in due:
        try:
            body = (
                "Reminder\n"
                f"{reminder['message']}\n"
                f"Due: {_format_timestamp(datetime.fromisoformat(reminder['run_at']))}"
            )
            send_message(to=WHATSAPP_OWNER_NUMBER, body=body)
            sent_ids.add(reminder["id"])
        except Exception:
            logger.exception("Failed to send reminder %s", reminder["id"])

    if not sent_ids:
        return

    with _STORE_LOCK:
        reminders = _load_reminders()
        sent_at = datetime.now().isoformat(timespec="seconds")
        for reminder in reminders:
            if reminder["id"] in sent_ids:
                reminder["sent_at"] = sent_at
        _save_reminders(reminders)


def send_daily_gmail_digest() -> None:
    """Send a proactive inbox summary if the daily digest is enabled."""
    if not WHATSAPP_OWNER_NUMBER:
        logger.debug("Daily digest skipped: WHATSAPP_OWNER_NUMBER is not set.")
        return

    try:
        summary = gmail.inbox_summary(limit=5)
        send_message(
            to=WHATSAPP_OWNER_NUMBER,
            body=f"Daily Gmail digest\n\n{summary}",
        )
    except EnvironmentError:
        logger.info("Daily Gmail digest skipped: Gmail credentials are not configured yet.")
    except Exception:
        logger.exception("Failed to send daily Gmail digest.")


def start_scheduler() -> None:
    """Start the background scheduler once per process."""
    global _scheduler

    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        process_due_reminders,
        "interval",
        seconds=max(SCHEDULER_POLL_SECONDS, 15),
        id="due-reminders",
        replace_existing=True,
    )

    if DAILY_GMAIL_DIGEST_ENABLED:
        _scheduler.add_job(
            send_daily_gmail_digest,
            CronTrigger(hour=DAILY_GMAIL_DIGEST_HOUR, minute=DAILY_GMAIL_DIGEST_MINUTE),
            id="daily-gmail-digest",
            replace_existing=True,
        )

    _scheduler.start()
    logger.info("Notification scheduler started.")


def shutdown_scheduler() -> None:
    """Stop the background scheduler cleanly."""
    global _scheduler

    if not _scheduler:
        return

    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Notification scheduler stopped.")
    _scheduler = None


def _parse_reminder_text(text: str) -> tuple[datetime | None, str | None]:
    match = _RELATIVE_PATTERN.match(text)
    if match:
        amount = int(match.group(1))
        unit = match.group(2).lower()
        message = match.group(3).strip()
        delta = _relative_delta(amount, unit)
        return datetime.now() + delta, message

    match = _ABSOLUTE_PATTERN.match(text)
    if match:
        when = match.group(1).replace("T", " ")
        message = match.group(2).strip()
        try:
            run_at = datetime.strptime(when, "%Y-%m-%d %H:%M")
        except ValueError:
            return None, None
        return run_at, message

    match = _TOMORROW_PATTERN.match(text)
    if match:
        hour_text, minute_text = match.group(1).split(":", 1)
        message = match.group(2).strip()
        now = datetime.now()
        run_at = (now + timedelta(days=1)).replace(
            hour=int(hour_text), minute=int(minute_text), second=0, microsecond=0
        )
        return run_at, message

    return None, None


def _relative_delta(amount: int, unit: str) -> timedelta:
    if unit.startswith("minute"):
        return timedelta(minutes=amount)
    if unit.startswith("hour"):
        return timedelta(hours=amount)
    return timedelta(days=amount)


def _load_reminders() -> list[dict[str, str]]:
    path = Path(REMINDER_STORE_PATH)
    if not path.exists():
        return []

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Reminder store is invalid JSON. Returning empty list.")
        return []

    if not isinstance(loaded, list):
        logger.warning("Reminder store is not a list. Returning empty list.")
        return []
    return loaded


def _save_reminders(reminders: list[dict[str, str]]) -> None:
    path = Path(REMINDER_STORE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(reminders, indent=2), encoding="utf-8")


def _format_timestamp(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M")
