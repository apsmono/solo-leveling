# Changelog

All notable changes to this project should be documented here in a curated, human-readable format.

Timestamp rule: use local device time in the format `YYYY-MM-DD HH-mm-ss`.

## Unreleased

### Added

- 2026-04-22 09-54-38 Added `docs/SESSION-RECAP-2026-04-22.md` capturing this session's WhatsApp setup guidance, Meta legal-verification research conclusions, and the API-setup UI troubleshooting notes for later review.
- 2026-04-22 09-54-38 Added `docs/PLAN-WITHOUT-WHATSAPP-2026-04-22.md` with a phased execution plan to keep project progress moving while WhatsApp integration is intentionally paused.
- 2026-04-21 21-52-07 Added `.github/workflows/ci.yml` GitHub Actions pipeline that runs all 23 tests on every push and pull request to `main`. Credential-gated live tests are automatically skipped in CI (no secrets needed). Establishes a continuous safety net for regression detection without manual test runs.
- 2026-04-21 21-52-07 Added `docs/TASK-MULTI-AI-003.md` defining the CI pipeline setup task with acceptance criteria, scope, and execution plan.
- 2026-04-21 19-30-19 Added `tests/test_integration_smoke.py` as a credential-aware integration smoke suite with router mocks, workflow and AI guardrails, optional live Notion/Drive/Gmail checks, and explicit skip messaging for missing credentials.
- 2026-04-21 19-30-19 Added `.github/prompts/research-ai-task.prompt.md`, `.github/prompts/executor-ai-task.prompt.md`, and `.github/prompts/quality-ai-task.prompt.md` so additional AI collaborators can be onboarded quickly with role-specific instructions.
- 2026-04-21 19-30-19 Added `docs/TASK-MULTI-AI-002-research.md` documenting integration entry points, credential constraints, smoke-matrix decisions, and implementation boundaries.
- 2026-04-21 13-04-19 Added `docs/TASK-MULTI-AI-002.md` as the next Monitor-AI task definition: a credential-aware integration smoke suite covering Notion, Drive, Gmail, router flows, and execution instructions that do not break when secrets are missing.
- 2026-04-21 12-10-00 Added one-command cross-device continuity helper: `scripts/device-sync.sh` with `switch-out`, `switch-in`, and `bootstrap-prompt` modes plus `prompts/cross-device-startup.prompt.txt` for consistent startup context on another device.
- 2026-04-21 11-35-00 Completed first multi-AI coordinated task (TASK-MULTI-AI-001): Implemented in-memory LRU search cache for library queries with automatic TTL expiration and invalidation. Warm cache hits are 100% faster (1.9ms → 0ms), exceeding 50% target. All 9 tests pass (3 new cache tests). Demonstrates full async handoff workflow: Research → Design → Implement → Validate → Merge across 4 feature branches with clear handoff summaries. Task completed in ~70 minutes wall-clock time.
- 2026-04-21 11-29-00 Added comprehensive multi-AI coordination framework: `docs/ai-team-coordination.md` defines team roles (Monitor AI, Executor, Research, Quality), task tracking system (issue → branch → PR → merge), communication protocol, git discipline, session memory flow, escalation paths, and success metrics. Establishes Monitor AI (Copilot) as coordinator for async multi-AI work.
- 2026-04-21 11-29-00 Added first multi-AI pilot task: `docs/TASK-MULTI-AI-001.md` specifies Library Search Optimization with detailed 5-phase execution flow (Research → Design → Implement → Validate → Merge). Shows exactly how AIs coordinate async via git branches, PR handoff summaries, and session memory. Ready for immediate execution.
- 2026-04-21 11-21-00 Added comprehensive "AI Team Organization" research to library: deep research bundle covering multi-agent coordination, five core roles (Strategic Planner, Executor, Coordinator, Reviewer, Domain Expert), task allocation patterns, handoff protocols, Project Manager AI responsibilities, and scaling from 1 to 10+ AIs. Auto-generated term definition, reference guide (strategies, patterns, open questions), and reasoning/thought entry.
- 2026-04-21 11-06-00 Completed MCP (Model Context Protocol) library entry with full enrichment: added term definition to `library/terms/`, comprehensive architecture reference to `library/references/`, three thought entries to `library/thoughts/` (strategic reasoning, phased adoption plan, recommendation), and replaced heuristic-placeholder content in the research bundle's Q/A, logic trail, and conclusion files with real MCP knowledge.
- 2026-04-21 11-06-00 Extended `_capture_research_bundle()` in `src/core/libraries.py` to automatically produce three supporting entries on every deep capture: a term definition (`library/terms/`), a reference file (`library/references/`), and a reasoning/thought entry (`library/thoughts/`). This is now the standard behavior for all future "add to library" deep captures.

### Changed (Earlier Sessions)

- 2026-04-21 19-30-19 Completed and validated MULTI-AI-002: hardened smoke coverage includes empty-result and malformed-payload cases, Gmail live smoke now avoids unintended interactive OAuth in headless runs unless explicitly enabled, Stage 9 cache performance test was stabilized for fast environments, and docs now include exact smoke-test commands and expected skip behavior.
- 2026-04-21 19-30-19 Updated active multi-AI planning state: `docs/TASK-MULTI-AI-002.md` marked `DONE`, `docs/ai-team-coordination.md` task board updated, and next coordinated candidate shifted to deployment readiness.
- 2026-04-21 13-04-19 Updated multi-AI planning docs after pilot completion: `AI_CONTEXT.md`, `docs/ai-team-coordination.md`, `docs/ai-working-notes.md`, and `docs/ai-knowledge/continuation-plan.md` now treat MULTI-AI-001 as completed and point to MULTI-AI-002 as the next coordinated task.
- 2026-04-21 13-00-07 Monitor AI normalized MULTI-AI-001 documentation state: `docs/TASK-MULTI-AI-001.md` now reflects `DONE` with completed acceptance criteria, and `docs/TASK-MULTI-AI-001-validation.md` no longer shows a stale pending changelog note.
- 2026-04-21 11-29-00 Updated `AI_CONTEXT.md` to add multi-AI team execution as active priority, referencing new coordination framework and first pilot task.
- 2026-04-21 11-29-00 Updated `docs/ai-working-notes.md` with session notes on multi-AI coordination framework establishment and AI Team Organization research completion.

- 2026-04-20 23-38-29 Added a production `Dockerfile` and `.dockerignore` for the FastAPI webhook runtime, plus README instructions that mount `library/` and `data/` so Stage 9 content and reminders persist outside the container.
- 2026-04-20 23-38-29 Added weekly Stage 9 maintenance support: `library maintenance` returns a cleanup checklist with live library coverage, `library maintenance schedule` reports the configured reminder slot, and the scheduler can send a recurring weekly WhatsApp maintenance reminder via new env vars.
- 2026-04-20 23-21-01 Added executable Stage 9 regression tests in `tests/test_stage9_libraries.py` for local validation rules, library entry writes, deep research-bundle capture, and indexed retrieval commands.
- 2026-04-20 23-16-38 Added Stage 9 indexed retrieval: `library/index.json` is now generated from `library/` contents, and new library commands can search indexed entries, find research bundles, and summarize bundle overviews.
- 2026-04-20 23-02-54 Added deep research-bundle capture flow for `add to library` / `add to my personal knowledge`: Stage 9 can now categorize incoming knowledge, define valuable information to track, search existing library entries, and save raw input, search history, research notes, Q/A, logic trail, and conclusion under `library/`.
- 2026-04-20 22-47-07 Added canonical local library structure under `library/` with subfolders: `profile/`, `terms/`, `books/`, `articles/`, `thoughts/`, and `references/`, plus `library/README.md` to define folder semantics and file naming.
- 2026-04-18 10-22-15 Added `docs/personal-library-formatting-guide.md`: comprehensive human-readable standard for all Stage 9 library entries covering 9-field property order, per-type formats (Profile, Terms, Books, Articles, Thoughts), Title Case naming, lowercase-hyphen tags (max 5), anti-mess guardrails, and weekly/monthly/quarterly maintenance checklists.
- 2026-04-18 10-22-15 Added formatting enforcement to `src/core/libraries.py`: `_apply_formatting_standard()` validates titles, tags, dates, and status on all uploads; `_ensure_title_case()` enforces consistent title casing; `_save_formatting_guide_to_library()` persists the guide to Notion.
- 2026-04-18 10-22-15 Added `library_guide` intent to router: WhatsApp users can send "library guide" to save the formatting standard as a reference page in their Notion library.
- 2026-04-18 09-34-07 Added `src/core/libraries.py` as the first Stage 9 command module, including handlers for profile, term, book, article, thought, and review flows with sensitive-data blocking for profile capture commands.
- 2026-04-18 09-03-43 Added `.editorconfig` and `.prettierrc` to lock Markdown indentation to 2-space spaces and preserve prose wrap, preventing VS Code's formatter from silently producing unstaged whitespace-only diffs on every edit.
- 2026-04-18 08-52-24 Added reusable shell templates under `config/zsh/` (`.zshrc.example`, `.zprofile.example`) based on the current device setup, sanitized for repo-safe reuse across machines and AI sessions.
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

### Changed (Foundation)

- 2026-04-20 23-34-40 Cleaned active Stage 9 documentation entry points so `docs/README.md` and `docs/personal-library-implementation-checklist.md` now describe the local `library/` workflow first, while keeping older Notion schema notes as historical reference only.
- 2026-04-20 23-16-38 Tightened Stage 9 field validation for core capture commands (`add term`, `book`, `article`, `thought`) and improved search output so research bundles resolve at bundle level instead of listing every internal file.
- 2026-04-20 23-02-54 Updated Stage 9 documentation and local library conventions so "add to library" now implies full research + categorization + processing workflow before writing to `library/`, with `library/research/` as the default bundle location for new knowledge types.
- 2026-04-20 22-47-07 Reworked `src/core/libraries.py` from Notion-backed Stage 9 captures to local filesystem storage; library commands now write/read markdown entries inside `library/` and `library_guide` saves to `library/references/`.
- 2026-04-20 22-47-07 Updated Stage 9 planning/context docs (`AI_CONTEXT.md`, `docs/ai-knowledge/continuation-plan.md`, `docs/personal-library-formatting-guide.md`, `docs/personal-knowledge-system-design.md`, `docs/personal-library-implementation-checklist.md`, `docs/ai-working-notes.md`) so "library" consistently means local folder `library/` and no longer implies a Notion library backend.
- 2026-04-18 09-34-07 Extended `src/core/router.py` with Stage 9 library intents and dispatch wiring, and expanded `help` output with new profile/library commands so the new handler module is reachable from WhatsApp text commands.
- 2026-04-18 09-31-05 Started implementation of the multi-agent delivery model: added branch naming, PR-first overlap handling, task-claim ownership, and handoff checklist rules in `AGENTS.md`, `.github/copilot-instructions.md`, and `docs/ai-knowledge/conventions.md`.
- 2026-04-18 09-31-05 Expanded Stage 9 documentation for personal profile capture aligned to MCP trends (schema-first contracts, profile lifecycle tools/resources/prompts, and sensitive-data exclusions) in `docs/personal-knowledge-system-design.md`, `docs/personal-library-implementation-checklist.md`, and `docs/ai-knowledge/continuation-plan.md`.
- 2026-04-18 09-20-15 Installed Meslo Powerlevel10k font on this device (`font-meslo-for-powerlevel10k`) and updated `.vscode/settings.json` terminal font family to `MesloLGS NF` with fallbacks so Oh My Zsh/Powerlevel10k glyphs render correctly in VS Code.
- 2026-04-18 08-56-01 Required all AI agents to re-read `AI_CONTEXT.md` and `docs/ai-knowledge/continuation-plan.md` after every `git pull` or `git push`, so agents never operate on stale project state after a sync. Rule added to `AGENTS.md`, `.github/copilot-instructions.md`, and `docs/ai-knowledge/conventions.md`.
- 2026-04-18 08-56-01 Fixed stale wording in `AGENTS.md` Current State section — now correctly reflects Stage 8 as complete and Stage 9 (Personal Knowledge Libraries) as the main active stage.
- 2026-04-18 08-52-24 Updated workspace terminal defaults in `.vscode/settings.json` to use macOS zsh login shell profile, MesloLGS NF terminal font, shell integration, and iTerm external terminal for consistent local behavior.
- 2026-04-18 08-52-24 Extended `docs/README.md` with a "Local Environment Templates" section so humans and AI agents can discover and apply terminal/zsh setup files quickly.
- 2026-04-18 09-06-27 Updated `.vscode/settings.json` terminal auto-approve command patterns to use this device workspace path (`/Users/macmini/Documents/projects/solo-leveling`) so terminal approvals match the current machine.
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
