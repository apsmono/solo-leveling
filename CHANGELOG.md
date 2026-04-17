# Changelog

All notable changes to this project should be documented here in a curated, human-readable format.

Timestamp rule: use local device time in the format `YYYY-MM-DD HH-mm-ss`.

## Unreleased

### Added

- 2026-04-17 15-49-02 Added Stage 8 starter workflow module `src/core/workflows.py` with the first chained command: summarise unread inbox and save the result as a Notion page.
- 2026-04-17 15-49-02 Added `docs/SETUP_SECRETS.md` with a practical TODO checklist for all required keys, per-service setup steps, and validation commands.
- 2026-04-17 15-28-52 Added Stage 6 notification scheduling: `src/core/scheduler.py` with persistent reminder storage, reminder-listing commands, WhatsApp delivery for due reminders, and an optional daily Gmail digest job powered by APScheduler.
- 2026-04-17 15-18-27 Created `docs/ai-knowledge/` folder with six focused files split out of `docs/ai-working-notes.md`: `build-history.md`, `conventions.md`, `error-log.md`, `integration-patterns.md`, `security-rules.md`, `continuation-plan.md`. Makes each topic independently findable and updatable.
- 2026-04-17 15-07-27 Added `docs/ai-working-notes.md`: persistent AI knowledge base capturing the full build history, every error encountered and its fix, integration patterns (WhatsApp/Notion/Drive/Gmail/AI agents), security rules, and continuation plan for Stages 6 and 8.

### Changed

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
