# Continuation Plan

Current state of the project and the next steps. Update this file whenever a stage is completed or a new workstream begins.

Last updated: 2026-04-17 21-05-00 (Stage 8 workflows expanded) → 2026-04-17 22-30-00 (Stage 9 research & design) → 2026-04-17 23-40-05 (Stage 9 database validation) → 2026-04-18 09-31-05 (Stage 9 implementation start: multi-agent git protocol + profile command design) → 2026-04-18 09-34-07 (Stage 9 code slice: library handlers + router wiring) → 2026-04-18 10-22-15 (formatting standard implemented) → 2026-04-20 22-47-07 (library term pivoted to local folder `library/`)

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
- **Stage 9 — Personal Knowledge Libraries (Phase 1 complete):**
  - Library handler module implemented (`src/core/libraries.py`) with 6 handler functions for profile, term, book, article, thought, and review captures.
  - Deep intake handler added for `add to library` / `add to my personal knowledge`; it categorizes input, identifies valuable information to track, searches existing library files, and writes a full research bundle with raw input, search history, research notes, Q/A, logic trail, and conclusion.
  - Router intents wired for all library commands.
  - Comprehensive formatting guide created (`docs/personal-library-formatting-guide.md`) covering: 9-field standard property order, per-type formats (Profile, Terms, Books, Articles, Thoughts), Title Case naming, lowercase-hyphen tags (max 5), anti-mess guardrails, weekly/monthly/quarterly maintenance checklists.
  - Formatting enforcement functions added: `_apply_formatting_standard()` (validates titles, tags, dates, status), `_ensure_title_case()` (consistent title casing), `_save_formatting_guide_to_library()` (saves guide under `library/references`).
  - New intent `library_guide` wired in router for WhatsApp trigger.
  - Library storage pivot completed: `library/` folder is now canonical, replacing Notion for Stage 9 library data.

## What Is Not Done Yet

- **Stage 9 — Personal Knowledge Libraries (Phase 2+):** Formatting guide is live. Next work is:
  1. **Filesystem indexing** — add fast search index for `library/` markdown entries.
  2. **Bundle retrieval UX** — add commands to summarize or reopen research bundles by topic.
  3. **Field-level validation** — add format constraints per library type (tag limits, status enums, required fields).
  4. **End-to-end testing** — manual WhatsApp tests for each library command family.
  5. **Library migration** — convert remaining legacy Notion-based assumptions/docs to local `library/` semantics.
  6. **Weekly maintenance scheduler** — automate cleanup checks (15-min checklist).
- **Tests:** `tests/` folder does not exist. Integration tests will need mock credentials or a test `.env`.
- **Deployment:** no `Dockerfile`, no CI/CD pipeline, no server. The Meta webhook requires a public HTTPS URL. Options: Railway, Fly.io, or any VPS with a reverse proxy.

## Blocking TODO (Secrets Setup)

- [ ] Complete all credential setup steps in `docs/SETUP_SECRETS.md`.
- [ ] Confirm `.env` exists and each integration can run one command successfully.
- [ ] Set `NOTION_WORKFLOW_PARENT_ID` so Stage 8 workflow output can be saved.

## Recommended Next Steps (in order)

1. Run manual WhatsApp command tests for each handler path and confirm corresponding writes/reads under `library/`.
2. Add bundle lookup/summarization commands for deep research captures.
3. Upgrade Stage 9 from basic file capture to indexed filesystem retrieval per library schema.
4. Add field-level validation and parser hardening for each command family.
5. Add a lightweight smoke test plan under `tests/` (or docs-first test checklist if code tests are deferred).
6. Add a `Dockerfile` and deploy to a permanent host.

## Latest Session Notes

### 2026-04-20 — Local Library Pivot

- Redefined `library` semantics for this repo: Stage 9 library storage is the local `library/` folder.
- Reworked `src/core/libraries.py` to write/search markdown entries in `library/profile`, `library/terms`, `library/books`, `library/articles`, `library/thoughts`, and `library/references`.
- Added local library structure and tracking files in repo (`library/README.md` plus `.gitkeep` files per section).
- Updated Stage 9 context/planning docs to local-library-first wording.
- Added deep research-bundle capture flow for `add to library` / `add to my personal knowledge`, preserving all logic, search history, Q/A, conclusions, and the valuable information-to-track list inside `library/`.

### 2026-04-18 — Multi-Agent Git Protocol & Stage 9 Formatting Implementation

**Multi-Agent Git Protocol & Stage 9 Formatting Implementation:**

- Established multi-agent Git collaboration rules: branch naming (`agent/<name>/<slug>/<stage>`), PR-first for overlaps, task-ownership claims, handoff checklists.
- Implemented comprehensive formatting standard (356-line markdown guide + 150 lines of Python enforcement code).
- Created `docs/personal-library-formatting-guide.md` with: universal rules (7 principles), 9-field standard property order, per-type format specs (Profile, Terms, Books, Articles, Thoughts), Title Case naming, lowercase-hyphen tags (max 5), anti-mess guardrails, weekly/monthly/quarterly maintenance checklists.
- Added `_apply_formatting_standard()` function to `src/core/libraries.py` for automatic validation of titles, tags, dates, and status on all library uploads.
- Added `_ensure_title_case()` helper to enforce consistent title casing across all entries.
- Added `_save_formatting_guide_to_library()` to persist the formatting guide as a reference entry.
- Wired `library_guide` intent in router so users can send "library guide" to WhatsApp to save the standard.
- Committed and pushed: `045539f docs: add Notion formatting standard for Stage 9 library`.
- Updated continuation plan with formatting standard completion and revised next steps (filesystem indexing, field validation, end-to-end testing).

**Previous Session Notes (2026-04-18 earlier):**

- Ran live schema audit for all four Stage 9 Notion databases.
- Current status: `Personal Knowledge Base`, `My Book Library`, and `Article Library` match planned schema; `Thought Drafts` uses `created_time` and `last_edited_time` for `Created` and `Last Updated`.
- Archived temporary validation rows from `Personal Knowledge Base` to keep production data clean.
- Implemented initial Stage 9 code in `src/core/libraries.py` with 6 handler functions for profile, term, book, article, thought, review.
- Wired router intents for all library commands.
- Historical note: Stage 9 previously used Notion page capture mode; this is now superseded by local `library/` storage.

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
