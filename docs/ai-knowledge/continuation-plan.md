# Continuation Plan

Current state of the project and the next steps. Update this file whenever a stage is completed or a new workstream begins.

Last updated: 2026-04-17 15-49-02

---

## What Is Done

- **Stage 1 — Foundation:** AI scaffold, changelog policy, planning docs, architecture docs, decisions log.
- **Stage 2 — WhatsApp bot:** `handler.py`, `client.py`, webhook verification, owner-number guard, router integration.
- **Stage 3 — Notion:** search, read page, create page, query database.
- **Stage 4 — Google Drive:** list files, read (export), create doc, move file.
- **Stage 5 — Gmail:** list unread, search, read message, inbox summary (read-only, OAuth2).
- **Stage 6 — Notifications:** APScheduler-based reminder scheduler with persistent JSON storage and optional daily Gmail digest delivery via WhatsApp.
- **Stage 7 — AI agent orchestration:** `dispatcher.py` with OpenAI + Anthropic; `ask` intent wired in router.

## What Is Not Done Yet

- **Stage 8 — Multi-step workflows:** initial workflow exists (`src/core/workflows.py`) for "summarise inbox and save to Notion", but Stage 8 is still in progress (needs more workflow patterns and robust confirmation/error flows).
- **Tests:** `tests/` folder does not exist. Integration tests will need mock credentials or a test `.env`.
- **Deployment:** no `Dockerfile`, no CI/CD pipeline, no server. The Meta webhook requires a public HTTPS URL. Options: Railway, Fly.io, or any VPS with a reverse proxy.

## Blocking TODO (Secrets Setup)

- [ ] Complete all credential setup steps in `docs/SETUP_SECRETS.md`.
- [ ] Confirm `.env` exists and each integration can run one command successfully.
- [ ] Set `NOTION_WORKFLOW_PARENT_ID` so Stage 8 workflow output can be saved.

## Recommended Next Steps (in order)

1. Set up all credentials: Meta Business verification, Notion integration token, Google service account JSON, Gmail OAuth2 consent screen, OpenAI or Anthropic API key.
2. Copy `.env.example` to `.env` and fill in all values.
3. Run the WhatsApp bot locally with `uvicorn src.integrations.whatsapp.handler:app --port 8000` and expose it via ngrok.
4. Complete `docs/SETUP_SECRETS.md` and verify each integration individually.
5. Validate Stage 8 starter command: `summarise my inbox and save to notion`.
6. Expand Stage 8 with at least 2 additional workflow chains.
7. Add a `Dockerfile` and deploy to a permanent host.
8. Add `tests/` with smoke tests per integration.

## Environment Variable Reference

Full list of all variables used across the codebase. Template in `.env.example`.

| Variable                     | Used By                     | Required                                 |
| ---------------------------- | --------------------------- | ---------------------------------------- |
| `WHATSAPP_PROVIDER`          | whatsapp/handler, client    | No (default: meta)                       |
| `WHATSAPP_OWNER_NUMBER`      | whatsapp/handler            | Yes                                      |
| `META_PHONE_NUMBER_ID`       | whatsapp/client             | Yes (if meta)                            |
| `META_ACCESS_TOKEN`          | whatsapp/client             | Yes (if meta)                            |
| `META_VERIFY_TOKEN`          | whatsapp/handler            | Yes (if meta)                            |
| `TWILIO_ACCOUNT_SID`         | whatsapp/client             | Yes (if twilio)                          |
| `TWILIO_AUTH_TOKEN`          | whatsapp/client             | Yes (if twilio)                          |
| `TWILIO_WHATSAPP_NUMBER`     | whatsapp/client             | Yes (if twilio)                          |
| `NOTION_API_TOKEN`           | notion/client               | Yes (for Notion)                         |
| `NOTION_WORKFLOW_PARENT_ID`  | core/workflows              | Yes (for Stage 8 Notion output)          |
| `GOOGLE_CREDENTIALS_PATH`    | gdrive/client, gmail/client | Yes (for Drive/Gmail)                    |
| `GMAIL_TOKEN_PATH`           | gmail/client                | No (default: .gmail_token.json)          |
| `REMINDER_STORE_PATH`        | core/scheduler              | No (default: data/reminders.json)        |
| `SCHEDULER_POLL_SECONDS`     | core/scheduler              | No (default: 30)                         |
| `DAILY_GMAIL_DIGEST_ENABLED` | core/scheduler              | No (default: false)                      |
| `DAILY_GMAIL_DIGEST_HOUR`    | core/scheduler              | No (default: 8)                          |
| `DAILY_GMAIL_DIGEST_MINUTE`  | core/scheduler              | No (default: 0)                          |
| `AGENT_PROVIDER`             | agents/dispatcher           | No (default: openai)                     |
| `OPENAI_API_KEY`             | agents/dispatcher           | Yes (if openai)                          |
| `OPENAI_MODEL`               | agents/dispatcher           | No (default: gpt-4o)                     |
| `ANTHROPIC_API_KEY`          | agents/dispatcher           | Yes (if anthropic)                       |
| `ANTHROPIC_MODEL`            | agents/dispatcher           | No (default: claude-3-5-sonnet-20241022) |
