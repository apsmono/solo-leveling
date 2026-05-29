# Telegram Webhook Overhaul — Design Spec

**Date:** 2026-05-29  
**Scope:** Fix critical bugs, add proactive messaging, and build webhook management CLI  
**Approach:** A (Solid Foundation)  

---

## 1. Context

The brain currently receives Telegram updates via `/webhook/telegram` and routes text messages through `route_command()`. The integration works for basic replies but has correctness issues and lacks management tooling.

### Current problems
1. **Secret checked in request body** — Telegram never sends `secret` in the JSON payload; the check is effectively a no-op when `TELEGRAM_WEBHOOK_SECRET` is set.
2. **No `update_id` deduplication** — Telegram retries on timeout; duplicate updates could trigger duplicate actions.
3. **No `/help` command** — Only `/start` is wired; `/help` falls through to the text handler.
4. **No proactive messaging** — The bot cannot send unprompted messages (reminders, autopilot notifications).
5. **No webhook management** — No scripts to register, inspect, or delete the webhook URL with Telegram.
6. **Telegram missing from health check** — `_handle_health()` does not verify the bot token.

---

## 2. Architecture

```
Telegram Bot API
       │ POST update
       │ + X-Telegram-Bot-Api-Secret-Token header
       ▼
┌─────────────────────────────┐
│  POST /webhook/telegram     │  ← app.py (header check)
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  process_update(payload)    │  ← webhook.py
│  • dedup by update_id       │
│  • extract & store chat_id  │
│  • route text to router     │
│  • reply to chat            │
└─────────────────────────────┘
              │
              ▼
┌─────────────────────────────┐
│  send_message(chat_id, text)│  ← client.py (proactive)
│  broadcast(text)            │
└─────────────────────────────┘
```

### File layout

```
src/integrations/telegram/
├── __init__.py          # exports: process_update, send_message, broadcast, get_stored_chat_ids
├── webhook.py           # webhook handler (dedup, /help, chat storage, reply routing)
├── client.py            # proactive messaging: send_message(), broadcast()
└── cli.py               # CLI script: set, info, delete, poll

data/
├── telegram_processed.json   # update_id deduplication log
└── telegram_chats.json       # chat ID store for proactive messaging
```

---

## 3. Detailed Design

### 3.1 Secret Check Fix (`app.py`)

**Current (broken):**
```python
secret = payload.get("secret", "")
if TELEGRAM_WEBHOOK_SECRET and secret != TELEGRAM_WEBHOOK_SECRET:
    ...
```

**Fixed:**
```python
from fastapi import Request

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, payload: dict[str, Any]) -> dict[str, str]:
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if TELEGRAM_WEBHOOK_SECRET and secret != TELEGRAM_WEBHOOK_SECRET:
        logger.warning("Telegram webhook received with invalid secret token header.")
        return {"status": "ok"}
    # ... rest of handler
```

The secret token is set via Telegram's `setWebhook` API (`secret_token` parameter). Telegram includes it in every webhook request as the `X-Telegram-Bot-Api-Secret-Token` header.

### 3.2 `update_id` Deduplication (`webhook.py`)

- **Storage:** `data/telegram_processed.json`
- **Format:** `{"update_ids": [123, 124, 125], "max_size": 1000}`
- **Behavior:**
  1. On incoming update, check if `update_id` is in `update_ids`
  2. If yes → log debug, return early (silently skip)
  3. If no → process update, append `update_id`, trim list to `max_size`
- **Persistence:** JSON file read on first check, written after every processed update

### 3.3 Chat ID Storage (`webhook.py`)

On every incoming message:
1. Extract `update.effective_chat.id`
2. Load `data/telegram_chats.json`
3. If chat ID exists → update `last_seen` timestamp
4. If new → append `{chat_id, first_seen, last_seen}`
5. Save file

**Format:**
```json
{
  "chats": [
    {
      "chat_id": 123456789,
      "first_seen": "2026-05-29T14:30:00+00:00",
      "last_seen": "2026-05-29T15:00:00+00:00"
    }
  ]
}
```

### 3.4 `/help` Command (`webhook.py`)

Add `CommandHandler("help", _handle_help)` alongside the existing `/start` handler.

```python
async def _handle_help(update: Any, _: Any) -> None:
    from src.core.router import _handle_help as get_help_text
    text = get_help_text("")
    if update.effective_message:
        await update.effective_message.reply_text(text[:4096])
```

### 3.5 Proactive Messaging (`client.py`)

```python
async def send_message(chat_id: int, text: str, parse_mode: str = "") -> bool:
    """Send a message to a specific chat. Return True on success."""

async def broadcast(text: str) -> dict[int, bool]:
    """Send to all stored chat IDs. Return {chat_id: success}."""

async def get_stored_chat_ids() -> list[int]:
    """Return list of stored chat IDs."""
```

- `send_message` uses `python-telegram-bot`'s `Bot.send_message()`
- Text > 4096 chars is split into multiple messages
- Failures are logged but do not raise

### 3.6 CLI Webhook Management (`cli.py`)

Run as: `python -m src.integrations.telegram.cli <command>`

| Command | Description |
|---------|-------------|
| `set <url>` | Register webhook URL with Telegram. Pass the **full URL** including path, e.g. `https://api.apsmono.com/webhook/telegram`. Sets `secret_token=TELEGRAM_WEBHOOK_SECRET` and `drop_pending_updates=True`. |
| `info` | Print current webhook info: URL, pending update count, last error timestamp, max connections. |
| `delete` | Delete webhook and drop pending updates. |
| `poll` | Start a `getUpdates` polling loop for local development without a public URL. Routes each received update through `process_update()` just like the webhook path. |

**Example:**
```bash
# Set webhook for production
python -m src.integrations.telegram.cli set https://api.apsmono.com/webhook/telegram

# Check status
python -m src.integrations.telegram.cli info

# Local dev fallback
python -m src.integrations.telegram.cli poll
```

### 3.7 Health Check (`router.py`)

Add Telegram to `_handle_health()`:

```
Telegram: ✅ (TELEGRAM_BOT_TOKEN set)
```

If the bot instance is available, also call `getWebhookInfo` and display:
- Webhook URL (if set)
- Pending updates count
- Last error (if any)

### 3.8 Reply Handling Improvements (`webhook.py`)

Current truncation: `reply[:4096]`

**New behavior:**
- If reply ≤ 4096 chars → send as one message
- If reply > 4096 chars → split on paragraph boundaries if possible, otherwise on newline, otherwise hard-split at 4096

---

## 4. Data & State

### `data/telegram_processed.json`
```json
{
  "update_ids": [123456789, 123456790, 123456791],
  "max_size": 1000
}
```

### `data/telegram_chats.json`
```json
{
  "chats": [
    {
      "chat_id": 123456789,
      "first_seen": "2026-05-29T14:30:00+00:00",
      "last_seen": "2026-05-29T15:00:00+00:00"
    }
  ]
}
```

Both files are created on first write. No migration needed (new feature).

---

## 5. Environment Variables

No new env vars. Existing vars in `config.py`:

| Variable | Purpose |
|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_WEBHOOK_SECRET` | Secret token for webhook verification (sent as `X-Telegram-Bot-Api-Secret-Token`) |

**Action:** Add these to `.env.example` (currently missing).

---

## 6. Testing

### Unit tests (`tests/test_telegram.py`)

| Test | What it verifies |
|------|-----------------|
| `test_webhook_secret_header` | Valid `X-Telegram-Bot-Api-Secret-Token` header is accepted |
| `test_webhook_invalid_secret_header` | Invalid/missing header returns 200 with no processing (fail-safe) |
| `test_webhook_dedup` | Same `update_id` twice → second is silently skipped |
| `test_webhook_stores_chat_id` | New chat ID is persisted to `telegram_chats.json` |
| `test_webhook_help_command` | `/help` command triggers `_handle_help` response |
| `test_send_message` | `send_message()` calls `Bot.send_message` |
| `test_broadcast` | `broadcast()` sends to all stored chat IDs |
| `test_cli_set` | `cli.set_webhook()` calls `setWebhook` with correct params |
| `test_cli_info` | `cli.get_info()` calls `getWebhookInfo` |
| `test_cli_delete` | `cli.delete_webhook()` calls `deleteWebhook` |

### Manual verification

1. Run `python -m src.integrations.telegram.cli set https://your-domain.com/webhook/telegram`
2. Send a message to the bot → should reply
3. Send `/help` → should show command list
4. Send a long message that produces a > 4096 char reply → should receive multiple messages
5. Run `python -m src.integrations.telegram.cli info` → should show webhook URL
6. Call `send_message()` from a Python shell → should deliver proactively

---

## 7. Edge Cases

| Scenario | Handling |
|----------|----------|
| `TELEGRAM_WEBHOOK_SECRET` not set | Accept all webhooks (dev mode) |
| `python-telegram-bot` not installed | Raise `EnvironmentError` with clear message |
| `TELEGRAM_BOT_TOKEN` not set | Raise `EnvironmentError` on any Telegram operation |
| Chat ID file corrupted | Log warning, treat as empty, recreate on next message |
| Processed ID file corrupted | Log warning, treat as empty, accept all updates |
| Bot receives non-text update (photo, sticker) | Silently ignore (return early) |
| `send_message()` fails (blocked, deleted chat) | Log error, return `False`, do not raise |
| Reply > 4096 chars | Split into multiple messages |

---

## 8. Future Work (Out of Scope)

- Admin HTTP endpoints for webhook management (`POST /admin/telegram/webhook/set`)
- Inline keyboards / callback queries
- Message editing (update previous bot messages)
- Media handling (photos, documents)
- Multi-user support (user-specific command permissions)

---

## 9. Open Questions

None. Design approved by user on 2026-05-29.
