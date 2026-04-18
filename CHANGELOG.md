# Changelog

All notable changes to this project should be documented here in a curated, human-readable format.

Timestamp rule: use local device time in the format `YYYY-MM-DD HH-mm-ss`.

## Unreleased

### Added

- 2026-04-17 21-52-34 Improved Notion robustness by normalizing page/database IDs in `src/integrations/notion/client.py` so API calls accept plain IDs, UUID-style IDs, full URLs, and slug+ID values (including `NOTION_WORKFLOW_PARENT_ID` from `.env`).
- 2026-04-17 21-36-18 Added MCP knowledge pack to `docs/personal-knowledge-system-design.md` including MCP definitions (host, client, server, tool, resource, prompt, schema-first contracts, capability negotiation) and a practical MCP adoption path for this repo.
- 2026-04-17 21-36-18 Added `Step 1.0: Notion Integration Setup (latest flow)` to `docs/personal-library-implementation-checklist.md` with explicit setup, verification, and troubleshooting sequence.
- 2026-04-17 21-28-27 Added a persistent "Notion Quick Review Checklist" and "Notion Pricing Note" to `docs/ai-knowledge/integration-patterns.md` so setup can be reviewed instantly without re-research.
- 2026-04-17 21-15-34 Researched self-development strategies and personal knowledge management systems. Created `docs/personal-knowledge-system-design.md` with: (1) self-development frameworks (deliberate practice, atomic habits, spaced repetition, Zettelkasten), (2) schema design for 4 library types (Knowledge Base, Books, Articles, Thoughts), (3) Notion database structure with fields and views, (4) Drive folder hierarchy, (5) WhatsApp command integration plan for Stage 9, (6) Phase-based implementation roadmap, and (7) success metrics.
- 2026-04-17 21-15-34 Created `docs/personal-library-implementation-checklist.md` with: (1) decision framework for quick-start vs full approach, (2) step-by-step Notion setup for 4 databases, (3) Google Drive folder structure, (4) manual testing workflow, (5) WhatsApp command integration guide, (6) code skeleton for `src/core/libraries.py`, and (7) Phase 4 AI enhancement roadmap.
- 2026-04-17 21-05-00 Expanded Stage 8 workflows with two new multi-step chains: `_workflow_inbox_summary_to_drive()` (Gmail inbox summary → Google Doc) and `_workflow_notion_query_to_drive()` (Notion search results → Google Doc). Updated router intent detection to recognize all three workflow patterns and expanded help text.
- 2026-04-17 15-49-02 Added Stage 8 starter workflow module `src/core/workflows.py` with the first chained command: summarise unread inbox and save the result as a Notion page.
- 2026-04-17 15-49-02 Added `docs/SETUP_SECRETS.md` with a practical TODO checklist for all required keys, per-service setup steps, and validation commands.
- 2026-04-17 15-28-52 Added Stage 6 notification scheduling: `src/core/scheduler.py` with persistent reminder storage, reminder-listing commands, WhatsApp delivery for due reminders, and an optional daily Gmail digest job powered by APScheduler.
- 2026-04-17 15-18-27 Created `docs/ai-knowledge/` folder with six focused files split out of `docs/ai-working-notes.md`: `build-history.md`, `conventions.md`, `error-log.md`, `integration-patterns.md`, `security-rules.md`, `continuation-plan.md`. Makes each topic independently findable and updatable.
- 2026-04-17 15-07-27 Added `docs/ai-working-notes.md`: persistent AI knowledge base capturing the full build history, every error encountered and its fix, integration patterns (WhatsApp/Notion/Drive/Gmail/AI agents), security rules, and continuation plan for Stages 6 and 8.

### Changed

- 2026-04-18 08-45-54 Clarified git sync policy language to explicit post-edit order across instruction files: always commit first, then push.
- 2026-04-18 08-43-42 Updated `.github/copilot-instructions.md`, `AGENTS.md`, and conventions notes to enforce git sync on every file-change cycle: pull before edits and push after completion.
- 2026-04-17 23-40-05 Audited all Stage 9 Notion databases against `docs/personal-library-implementation-checklist.md`; confirmed `Personal Knowledge Base`, `My Book Library`, and `Article Library` align with planned schema, and noted `Thought Drafts` uses auto-managed timestamp properties (`created_time`, `last_edited_time`) for `Created` and `Last Updated`.
- 2026-04-17 23-40-05 Cleaned validation artifacts in Notion by archiving temporary test rows (`Test Concept A`, `Test Concept B`) from `Personal Knowledge Base` after relation behavior verification.
- 2026-04-18 08-36-18 Added a mandatory git preflight step to preparation docs: run `git fetch --all --prune && git status -sb` before setup, and use `git pull --ff-only` when behind remote.
- 2026-04-17 16-04-26 Clarified `AGENTS.md` with an explicit absolute session policy: **ALWAYS read before starting** and **ALWAYS write after finishing**.
- 2026-04-17 15-49-02 Updated router intent handling and help output to support Stage 8 workflow commands; added `NOTION_WORKFLOW_PARENT_ID` to `.env.example` and config.
- 2026-04-17 15-49-02 Updated AI context and continuation docs to keep a visible blocking TODO for secrets setup and to mark Stage 8 as in progress.
- 2026-04-17 15-28-52 Updated the webhook app, router help text, `.env.example`, `.gitignore`, and Stage 6 documentation so reminders now run as a background scheduler inside the existing FastAPI process and runtime reminder data stays out of git.
- 2026-04-17 15-18-27 Converted `docs/ai-working-notes.md` from a monolithic file into a short index that links to `docs/ai-knowledge/`. Updated `docs/README.md` to list all new files.
- 2026-04-17 15-11-19 Updated `AGENTS.md` to reflect actual implementation state (Stages 1–5 and 7 done) and added a **Persistent Memory Rule** requiring all AI agents to write session findings back to the repo before finishing — supports multi-device and multi-AI-tool workflows.
- 2026-04-17 15-11-19 Updated `AI_CONTEXT.md` to reflect actual current phase, corrected priorities to Stages 6 and 8, added completed-stages table, and made `docs/ai-working-notes.md` a first-class source-of-truth entry.

- 2026-04-17 14-40-46 Added `docs/architecture/command-center.md` with full brain architecture, data flow, and staged implementation plan.
- 2026-04-17 14-40-46 Added `docs/architecture/integrations.md` with integration contracts for WhatsApp, Notion, Google Drive, Gmail, and notifications.
- 2026-04-17 14-58-15 Implemented Stages 3–5 and 7: Notion search client, Google Drive list/read/create client, Gmail read-only client with inbox summary, and AI agent dispatcher (OpenAI + Anthropic).
- 2026-04-17 14-58-15 Wired all integrations into the command router; replaced placeholder stubs with real calls; added `ask` intent for direct AI queries.
- 2026-04-17 14-45-47 Scaffolded Stage 2 WhatsApp command bot: `src/integrations/whatsapp/handler.py`, `client.py`, `src/core/router.py`, `src/core/config.py`, `requirements.txt`, `.env.example`, and `.gitignore`.
- 2026-04-17 14-45-47 Added `docs/decisions/002-whatsapp-approach.md` recording the choice of Meta Cloud API as the primary WhatsApp provider.
- 2026-04-17 14-40-46 Added `docs/decisions/001-command-center-scope.md` recording the formal decision to redefine this repo as the central command center.
- 2026-04-17 14-34-16 Added a reusable `docs/` planning structure for self-development, finance, habits, and review workflows.
- 2026-04-17 14-34-16 Added a decision log template so future strategic and structural choices can be recorded consistently.
- 2026-04-17 14-30-41 Added the initial AI-friendly workspace scaffold, including repository instructions, reusable prompts, and workspace settings.
- 2026-04-17 14-30-41 Added a changelog standard and policy so future AI and human updates remain consistent and readable.

### Changed

- 2026-04-17 14-40-46 Expanded repository scope from personal planning to full command-center and integration brain; updated `README.md`, `AGENTS.md`, `AI_CONTEXT.md`, and `docs/README.md` to reflect the new mission.

### Docs

- 2026-04-17 14-34-16 Documented the new planning-document map so AI and human contributors have clear entry points for strategy work.
- 2026-04-17 14-30-41 Documented the repository source-of-truth files and the expectation that documentation and descriptions must be updated together with notable changes.

### Decisions

- 2026-04-17 14-40-46 Decided to redefine this repository as the central brain and command center; integration with WhatsApp, Notion, GDrive, and Gmail is now in scope (see `docs/decisions/001`).
- 2026-04-17 14-30-41 Adopted a curated changelog model inspired by Keep a Changelog, but with required local timestamps on each notable entry.
