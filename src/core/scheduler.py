"""
Notification scheduler for proactive reminders and digest jobs.

Stage 6 introduces a small persistent reminder system backed by a JSON file so
scheduled reminders survive process restarts. Jobs are executed by APScheduler
inside the same process as the webhook server.

## Container restart behaviour

The scheduler is fully stateless across restarts: all reminder state lives in
`data/reminders.json` (path controlled by REMINDER_STORE_PATH env var).

On container restart:
  - start_scheduler() is called from the lifespan hook, creating a fresh
    BackgroundScheduler instance.
  - process_due_reminders() is polled immediately on the first interval tick
    and sends any reminder whose run_at timestamp has already passed.
  - No reminder is lost as long as the `data/` mount is preserved between
    container runs (volume bind or named Docker volume).

If `data/` is NOT mounted persistently (e.g., ephemeral container), all
unsent reminders will be lost on restart. This is expected and documented
behaviour; mount the volume to avoid it.

APScheduler jobs (due-reminders, daily-digest, library-maintenance) are
always re-registered on startup — there is no persistent job store. The
CronTrigger jobs use wall-clock time so they will fire on schedule whenever
the process is running.
"""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from uuid import uuid4

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
except ModuleNotFoundError:
    BackgroundScheduler = None
    CronTrigger = None

from src.core.config import (
    AUTOPILOT_ENABLED,
    AUTOPILOT_TICK_SECONDS,
    DAILY_GMAIL_DIGEST_ENABLED,
    DAILY_GMAIL_DIGEST_HOUR,
    DAILY_GMAIL_DIGEST_MINUTE,
    LIBRARY_MAINTENANCE_DAY,
    LIBRARY_MAINTENANCE_ENABLED,
    LIBRARY_MAINTENANCE_HOUR,
    LIBRARY_MAINTENANCE_MINUTE,
    REMINDER_STORE_PATH,
    SCHEDULER_POLL_SECONDS,
    USE_FIRESTORE_REMINDERS,
)
from src.core.libraries import format_library_maintenance_summary

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


# ---------------------------------------------------------------------------
# Reminder store abstraction
# ---------------------------------------------------------------------------

class _ReminderStore(ABC):
    @abstractmethod
    def create(self, message: str, run_at: datetime) -> dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    def list_pending(self) -> list[dict[str, str]]:
        raise NotImplementedError

    @abstractmethod
    def mark_sent(self, ids: set[str]) -> None:
        raise NotImplementedError


class _JsonReminderStore(_ReminderStore):
    def create(self, message: str, run_at: datetime) -> dict[str, str]:
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
        return reminder

    def list_pending(self) -> list[dict[str, str]]:
        return [item for item in _load_reminders() if not item.get("sent_at")]

    def mark_sent(self, ids: set[str]) -> None:
        with _STORE_LOCK:
            reminders = _load_reminders()
            sent_at = datetime.now().isoformat(timespec="seconds")
            for reminder in reminders:
                if reminder["id"] in ids:
                    reminder["sent_at"] = sent_at
            _save_reminders(reminders)


class _FirestoreReminderStore(_ReminderStore):
    def create(self, message: str, run_at: datetime) -> dict[str, str]:
        from src.integrations.firebase import firestore as fb

        doc_id = fb.create_reminder_doc(message, run_at)
        return {
            "id": doc_id,
            "message": message.strip(),
            "run_at": run_at.isoformat(timespec="seconds"),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "sent_at": "",
        }

    def list_pending(self) -> list[dict[str, str]]:
        from src.integrations.firebase import firestore as fb

        docs = fb.list_pending_reminders()
        results = []
        for doc in docs:
            run_at = doc.get("run_at")
            if isinstance(run_at, datetime):
                run_at = run_at.isoformat(timespec="seconds")
            results.append({
                "id": doc["id"],
                "message": doc.get("message", ""),
                "run_at": run_at or "",
                "created_at": "",
                "sent_at": "",
            })
        return results

    def mark_sent(self, ids: set[str]) -> None:
        from src.integrations.firebase import firestore as fb

        for doc_id in ids:
            try:
                fb.mark_reminder_sent(doc_id)
            except Exception:
                logger.exception("Failed to mark reminder %s as sent in Firestore", doc_id)


def _get_store() -> _ReminderStore:
    if USE_FIRESTORE_REMINDERS:
        return _FirestoreReminderStore()
    return _JsonReminderStore()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

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
    store = _get_store()
    reminder = store.create(message, run_at)
    logger.info("Reminder scheduled for %s: %s", reminder["run_at"], reminder["message"])
    return reminder


def format_pending_reminders() -> str:
    store = _get_store()
    reminders = store.list_pending()
    if not reminders:
        return "No pending reminders."

    lines = ["Pending reminders:\n"]
    for index, reminder in enumerate(sorted(reminders, key=lambda item: item["run_at"]), start=1):
        lines.append(f"{index}. {_format_timestamp(datetime.fromisoformat(reminder['run_at']))}")
        lines.append(f"   {reminder['message']}")
    return "\n".join(lines)


def process_due_reminders() -> None:
    """Send any reminders whose due time has passed."""
    store = _get_store()
    now = datetime.now()
    due = [
        item for item in store.list_pending()
        if item.get("run_at") and datetime.fromisoformat(item["run_at"]) <= now
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
            logger.info("Reminder due: %s", body)
            sent_ids.add(reminder["id"])
        except Exception:
            logger.exception("Failed to send reminder %s", reminder["id"])

    if sent_ids:
        store.mark_sent(sent_ids)


def send_daily_gmail_digest() -> None:
    """Log a proactive inbox summary if the daily digest is enabled."""

    try:
        from src.integrations.gmail import client as gmail

        summary = gmail.inbox_summary(limit=5)
        logger.info("Daily Gmail digest:\n%s", summary)
    except EnvironmentError:
        logger.info("Daily Gmail digest skipped: Gmail credentials are not configured yet.")
    except Exception:
        logger.exception("Failed to send daily Gmail digest.")


def handle_library_maintenance_command(text: str) -> str:
    normalized = text.strip().lower()
    if normalized in {"library maintenance schedule", "library maintenance status", "maintenance schedule"}:
        return format_library_maintenance_schedule()
    return format_library_maintenance_summary()


def send_weekly_library_maintenance() -> None:
    try:
        logger.info("Weekly library maintenance reminder:\n%s", format_library_maintenance_summary())
    except Exception:
        logger.exception("Failed to send weekly library maintenance reminder.")


def process_autopilot_tick() -> None:
    """Execute one tick of the autopilot loop if enabled."""
    if not AUTOPILOT_ENABLED:
        return
    try:
        from src.autopilot.loop import get_loop

        get_loop().tick()
    except Exception:
        logger.exception("Autopilot tick failed.")


def start_scheduler() -> None:
    """Start the background scheduler once per process."""
    global _scheduler

    if BackgroundScheduler is None or CronTrigger is None:
        logger.warning("Scheduler start skipped: apscheduler is not installed.")
        return

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

    if AUTOPILOT_ENABLED:
        _scheduler.add_job(
            process_autopilot_tick,
            "interval",
            seconds=max(AUTOPILOT_TICK_SECONDS, 15),
            id="autopilot-tick",
            replace_existing=True,
        )
        logger.info("Autopilot tick scheduled every %s seconds.", max(AUTOPILOT_TICK_SECONDS, 15))

    if DAILY_GMAIL_DIGEST_ENABLED:
        _scheduler.add_job(
            send_daily_gmail_digest,
            CronTrigger(hour=DAILY_GMAIL_DIGEST_HOUR, minute=DAILY_GMAIL_DIGEST_MINUTE),
            id="daily-gmail-digest",
            replace_existing=True,
        )

    if LIBRARY_MAINTENANCE_ENABLED:
        _scheduler.add_job(
            send_weekly_library_maintenance,
            CronTrigger(
                day_of_week=_normalize_day_of_week(LIBRARY_MAINTENANCE_DAY),
                hour=LIBRARY_MAINTENANCE_HOUR,
                minute=LIBRARY_MAINTENANCE_MINUTE,
            ),
            id="weekly-library-maintenance",
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


def _normalize_day_of_week(value: str) -> str:
    allowed = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
    normalized = value.strip().lower()[:3]
    return normalized if normalized in allowed else "sun"


def format_library_maintenance_schedule() -> str:
    status = "enabled" if LIBRARY_MAINTENANCE_ENABLED else "disabled"
    return (
        "Library maintenance schedule\n"
        f"• Status: {status}\n"
        f"• Day: {_normalize_day_of_week(LIBRARY_MAINTENANCE_DAY)}\n"
        f"• Time: {LIBRARY_MAINTENANCE_HOUR:02d}:{LIBRARY_MAINTENANCE_MINUTE:02d}\n"
        "• Command: library maintenance"
    )
