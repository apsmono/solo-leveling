# Integration Patterns

Working patterns, gotchas, and setup notes for every service integrated into the command center.

## WhatsApp (Meta Cloud API)

- Webhook is a FastAPI app (`src/integrations/whatsapp/handler.py`).
- Meta sends a GET for webhook verification — uses `META_VERIFY_TOKEN`.
- Meta sends a POST with message payloads; extract via `entry[0].changes[0].value.messages[0]`.
- **Security:** always check `message["from"]` against `WHATSAPP_OWNER_NUMBER` before processing anything. Messages from other numbers are silently ignored.
- Twilio fallback: switch with `WHATSAPP_PROVIDER=twilio` env var; no code change needed.
- To run locally: `uvicorn src.integrations.whatsapp.handler:app --port 8000` with ngrok to expose a public HTTPS URL.
- Meta webhook URL must be set in the Meta Developer Console under WhatsApp > Configuration.

## Notion (notion-client SDK)

- Auth: internal integration token (`NOTION_API_TOKEN`), created at notion.so/my-integrations.
- **The integration must be explicitly invited to each page/database in Notion before it can access it** — this is a common gotcha.
- `client.search()` returns both pages and databases; filter by `item["object"]`.
- Title extraction differs for pages vs databases — see `_extract_title()` helper in `client.py`.
- `blocks.children.list()` paginates; current implementation fetches first page only. Add pagination when dealing with long documents.
- Notion IDs in this repo are now normalized automatically: plain 32-char IDs, UUID-style IDs, full URLs, and slug+ID values are accepted by the Notion client.

### Notion Quick Review Checklist (Persistent)

Use this checklist whenever you want to re-check Notion setup quickly.

1. Create internal integration in Notion and copy token.
2. Set `NOTION_API_TOKEN` in `.env`.
3. Create/open the target parent page in Notion (for workflow outputs).
4. Copy page ID from URL and set `NOTION_WORKFLOW_PARENT_ID` in `.env`.
5. Invite the integration to the parent page (and each database it should access).
6. Verify with command: `notion project`.
7. Verify workflow write with command: `summarise my inbox and save to notion`.

### Notion Pricing Note

- Notion API integration itself does not require a paid Notion plan for basic use.
- The free plan is usually enough for personal integrations and small-scale usage.
- Paid plans are only needed if you want advanced workspace/team/admin features, not just API access.

## Google Drive (google-api-python-client)

- Auth: service account JSON (`GOOGLE_CREDENTIALS_PATH`).
- **Service accounts do NOT work for Gmail** — Gmail requires OAuth2 user credentials (separate pattern below).
- `files().export()` only works for Google Docs/Sheets/Slides; binary files need `files().get_media()`.
- To create a Google Doc with content: create an empty doc first, then update with `MediaInMemoryUpload`.
- Scopes: `drive.readonly` for read, `drive.file` for create/update of files the app owns.

## Gmail (Google OAuth2)

- **Requires OAuth2, not a service account.** Gmail API acts on behalf of a user and cannot be accessed by a service account unless domain-wide delegation is configured (complex, not done here).
- First run opens a browser for user authorization; the token is saved to `.gmail_token.json` (in `.gitignore`).
- `.gmail_token.json` must never be committed — it grants full read access to the inbox.
- `messages().list()` returns only `{id, threadId}`; always call `messages().get()` for actual content.
- `format="metadata"` with `metadataHeaders` is faster for summaries; use `format="full"` only when the body is needed.
- Body decoding: base64url-encoded. Decode with `base64.urlsafe_b64decode(data + "==")` (the `==` padding is required).
- Multipart messages: recurse through `parts` to find `text/plain`.

## AI Agents (OpenAI / Anthropic)

- Switch provider with `AGENT_PROVIDER=openai` or `AGENT_PROVIDER=anthropic` env var; no code change needed.
- Models default to `gpt-4o` and `claude-3-5-sonnet-20241022`; override via `OPENAI_MODEL` / `ANTHROPIC_MODEL` env vars.
- Temperature set to 0.3 for consistent, practical responses (well-suited to command-center tasks).
- The system prompt in `dispatcher.py` instructs the agent to respond in plain paragraphs optimized for WhatsApp (no markdown tables, short sentences).
- Both `openai` and `anthropic` are lazily imported inside functions — only the active provider's library needs to be installed.

## Notifications / Scheduler

- Stage 6 is implemented in `src/core/scheduler.py` using APScheduler.
- The scheduler runs inside the FastAPI webhook process via app lifespan hooks, so reminders work whenever the webhook server is running.
- Reminder jobs are persisted to `data/reminders.json` so they survive restarts.
- Supported command formats:
  - `remind me in 30 minutes to stretch`
  - `remind me tomorrow at 09:00 to review goals`
  - `remind me at 2026-04-18 08:30 to plan the day`
  - `reminders`
- Optional daily Gmail digest sends `gmail.inbox_summary()` to WhatsApp on a cron schedule when `DAILY_GMAIL_DIGEST_ENABLED=true`.
- If Gmail credentials are missing, the digest job skips gracefully and logs the reason instead of crashing the scheduler.

## Workflows / Composition (Stage 8 Starter)

- Stage 8 started in `src/core/workflows.py`.
- Starter chain is implemented for: `summarise my inbox and save to notion`.
- Chain behavior:
  1. Calls Gmail summary helper.
  2. Creates a Notion page using `NOTION_WORKFLOW_PARENT_ID`.
- Setup dependency: workflow is blocked until secrets are configured. Use `docs/SETUP_SECRETS.md`.
- Intent-detection rule in router runs compound workflow matching before single-step keyword matching, because terms like "notion" and "inbox" overlap with existing intents.
