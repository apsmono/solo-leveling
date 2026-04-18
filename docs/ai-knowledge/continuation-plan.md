# Continuation Plan

Current state of the project and the next steps. Update this file whenever a stage is completed or a new workstream begins.

Last updated: 2026-04-17 21-05-00 (Stage 8 workflows expanded) → 2026-04-17 22-30-00 (Stage 9 research & design) → 2026-04-17 23-40-05 (Stage 9 database validation) → 2026-04-18 09-31-05 (Stage 9 implementation start: multi-agent git protocol + profile command design) → 2026-04-18 09-34-07 (Stage 9 code slice: library handlers + router wiring)

---

## What Is Done

- **Stage 1 — Foundation:** AI scaffold, changelog policy, planning docs, architecture docs, decisions log.
- **Stage 2 — WhatsApp bot:** `handler.py`, `client.py`, webhook verification, owner-number guard, router integration.
- **Stage 3 — Notion:** search, read page, create page, query database.
- **Stage 4 — Google Drive:** list files, read (export), create doc, move file.
- **Stage 5 — Gmail:** list unread, search, read message, inbox summary (read-only, OAuth2).
- **Stage 6 — Notifications:** APScheduler-based reminder scheduler with persistent JSON storage and optional daily Gmail digest delivery via WhatsApp.
- **Stage 7 — AI agent orchestration:** `dispatcher.py` with OpenAI + Anthropic; `ask` intent wired in router.
- **Stage 8 — Multi-step workflows:** three workflow chains implemented in `src/core/workflows.py`:
  - Summarise unread inbox → save as Notion page
  - Summarise unread inbox → save as Google Doc
  - Query Notion database → export results as Google Doc

## What Is Not Done Yet

- **Stage 9 — Personal Knowledge Libraries (Phase 3+):** Database setup and schema validation are complete. Next work is implementation of WhatsApp command handlers in `src/core/libraries.py` and router wiring in `src/core/router.py`.
- **Tests:** `tests/` folder does not exist. Integration tests will need mock credentials or a test `.env`.
- **Deployment:** no `Dockerfile`, no CI/CD pipeline, no server. The Meta webhook requires a public HTTPS URL. Options: Railway, Fly.io, or any VPS with a reverse proxy.

## Blocking TODO (Secrets Setup)

- [ ] Complete all credential setup steps in `docs/SETUP_SECRETS.md`.
- [ ] Confirm `.env` exists and each integration can run one command successfully.
- [ ] Set `NOTION_WORKFLOW_PARENT_ID` so Stage 8 workflow output can be saved.

## Recommended Next Steps (in order)

1. Run manual WhatsApp command tests for each handler path and confirm corresponding Notion writes/reads.
2. Upgrade Stage 9 from page-capture mode to database-property writes per library schema.
3. Add field-level validation and parser hardening for each command family.
4. Add a lightweight smoke test plan under `tests/` (or docs-first test checklist if code tests are deferred).
5. Add a `Dockerfile` and deploy to a permanent host.

## Latest Session Notes

- Ran live schema audit for all four Stage 9 Notion databases.
- Current status: `Personal Knowledge Base`, `My Book Library`, and `Article Library` match planned schema; `Thought Drafts` uses `created_time` and `last_edited_time` for `Created` and `Last Updated`.
- Archived temporary validation rows (`Test Concept A`, `Test Concept B`) from `Personal Knowledge Base` to keep production data clean.
- Started implementation with explicit multi-agent Git branch/PR/task-claim protocol in core instruction docs.
- Added MCP-aligned personal profile scope to Stage 9 docs (`skills`, `interests`, `domains`, `learning priorities`, `focus themes`) with sensitive-data exclusions.
- Implemented initial Stage 9 code in `src/core/libraries.py` and router wiring for intents: `library_profile`, `library_term`, `library_book`, `library_article`, `library_thought`, `library_review`.
- Current Stage 9 code path stores captures as Notion pages under `NOTION_WORKFLOW_PARENT_ID` for immediate usability; database-structured writes remain the next upgrade slice.

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
