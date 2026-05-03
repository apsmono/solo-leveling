# Changelog

All notable changes to this project should be documented here in a curated, human-readable format.

Timestamp rule: use local device time in the format `YYYY-MM-DD HH-mm-ss`.

Release section template (use when publishing a new git tag):

```md
## [vX.Y.Z] - YYYY-MM-DD

### Added

- YYYY-MM-DD HH-mm-ss Added ...

### Changed

- YYYY-MM-DD HH-mm-ss Changed ...

### Fixed

- YYYY-MM-DD HH-mm-ss Fixed ...

### Docs

- YYYY-MM-DD HH-mm-ss Updated docs ...

### Decisions

- YYYY-MM-DD HH-mm-ss Decision summary (link to docs/decisions/NNN-*.md)
```

Release step: move completed entries from `Unreleased` into the new version section and keep original per-entry timestamps unchanged.

## Unreleased

### Added

- 2026-05-03 16-45-00 Added Firebase ecosystem integration: `src/integrations/firebase/auth.py` (ID token verification with single-user email gate) and `src/integrations/firebase/firestore.py` (reminders + command logging collections). Firestore usage is gated by `USE_FIRESTORE_REMINDERS` env var; JSON file fallback remains active by default.
- 2026-05-03 23-22-24 Added Autopilot Phase 1 MVP: `src/autopilot/` package with loop, tools, governor, and planner. Supports `autopilot start: <goal>`, `autopilot status`, `autopilot pause`, `autopilot approve` commands. Tools: `read`, `bash`, `gmail_read`, `library_index`. Governor enforces RL-based safety gates aligned with `docs/ai-employer-operating-system.md`. Kimi API wired via `litellm` in `src/agents/kimi_client.py` using existing `litellm_config.yaml`. Scheduler tick job `autopilot-tick` runs every `AUTOPILOT_TICK_SECONDS` when `AUTOPILOT_ENABLED=true`. Tests in `tests/test_autopilot.py` (16 passing).
- 2026-05-03 16-45-00 Added versioned REST API under `/api/v1`: `src/api/dashboard.py` (library stats + integration health), `src/api/commands.py` (command history from Firestore), `src/api/reminders.py` (list/create/delete reminders). All dashboard endpoints require Firebase Auth Bearer token via `src/api/deps.py`.
- 2026-05-03 16-45-00 Added static dashboard frontend under `frontend/` for GitHub Pages deployment: landing page with command input, auth-gated dashboard with library overview, integration health, recent commands, reminder manager, and command sender. Built with vanilla JS, no build step. Added `.github/workflows/deploy-dashboard.yml` for automatic Pages deployment on push to `main`.
- 2026-05-03 16-45-00 Added CORS middleware to `src/app.py` allowing `FRONTEND_ORIGIN` and localhost dev servers.
- 2026-05-03 16-45-00 Added monorepo scaffolding: `subprojects/scrapers/`, `subprojects/microservices/example-service/`, and `docker-compose.yml` for MacMini backend orchestration.
- 2026-05-03 16-45-00 Added comprehensive test coverage: `tests/test_firebase.py` (auth + firestore, 9 tests), `tests/test_dashboard_api.py` (11 tests), `tests/test_telegram.py` (4 tests). Full suite now 59 tests (3 credential-gated skips).
- 2026-05-03 23-31-03 Replaced `frontend/index.html` with a public portfolio landing page. New `frontend/portfolio.css` provides dark-mode responsive styles. Sections: Hero, About, Projects, Skills, Contact, Footer. Includes mobile hamburger menu, smooth scroll, and placeholder content with `<!-- EDIT -->` markers for easy customization. Dashboard link preserved in nav and footer.
- 2026-05-03 16-45-00 Added Firebase, Telegram, and CORS environment variables to `src/core/config.py` and updated health check in `src/core/router.py` to report Firebase status.

### Changed

- 2026-05-03 16-45-00 Refactored `src/core/scheduler.py` with `_ReminderStore` abstraction: `_JsonReminderStore` (existing JSON file behavior) and `_FirestoreReminderStore` (new Firestore backend). Store selection is automatic based on `USE_FIRESTORE_REMINDERS` flag. All public scheduler functions (`create_reminder`, `format_pending_reminders`, `process_due_reminders`) work transparently with either backend.
- 2026-05-03 16-45-00 Updated `src/core/router.py` `route_command()` to accept optional `source` parameter and log commands to Firestore when `USE_FIRESTORE_REMINDERS` is enabled.
- 2026-05-03 16-45-00 Updated `.github/workflows/ci.yml` to run all five test modules (`test_stage9_libraries`, `test_integration_smoke`, `test_firebase`, `test_dashboard_api`, `test_telegram`).

### Fixed

- 2026-04-23 19-52-00 Corrected `docs/TASK-MULTI-AI-003.md` status from IN_PROGRESS to DONE with all 6 acceptance criteria checked. Task was completed 2026-04-21 (commit 7227075) but documentation was not updated at handoff; now synchronized with actual state (`.github/workflows/ci.yml` fully implemented, tests running green in CI).
- 2026-04-23 18-38-04 Added `docs/research/deployable-ai-short-context-2026-04-23.md`: research-backed execution model for short deployable AI context plus detailed per-AI task briefs (objective, scope, editable files, commands, acceptance criteria, evidence, handoff). Includes copy-paste templates for orchestrator/worker/validator/release roles and anti-patterns to reduce ambiguity and rework.
- 2026-04-23 13-41-44 Releasing development → main: 6 commits encompassing Railway deployment docs, health verification guide, deployment workflow, live status report, release checklist, and CI dual-branch wiring.
- 2026-04-23 13-38-36 Added `docs/RAILWAY_LIVE_STATUS.md`: live production deployment status report verifying Railway instance `https://solo-leveling-production-36c8.up.railway.app` is running (HTTP 200, FastAPI responding, webhook endpoint active, authorization checks working). Documents test results, validation checklist, and next steps for confirming full integration health via WhatsApp or local testing.

### Changed

- 2026-04-24 08-56-31 Migrated runtime entrypoint from WhatsApp webhook to generic FastAPI app (`src/app.py`) and updated `Dockerfile` command to `src.app:app` so deployments run interface-agnostic command APIs.
- 2026-04-24 08-56-31 Simplified AI dispatch to Gemini-only in `src/agents/dispatcher.py` and removed OpenAI/Anthropic runtime config paths from `src/core/router.py`, `.env.example`, and continuation docs.
- 2026-04-24 08-41-46 Revised core planning docs (`AI_CONTEXT.md`, `README.md`, `docs/ai-knowledge/continuation-plan.md`, `docs/architecture/command-center.md`, `docs/architecture/integrations.md`, `docs/SETUP_SECRETS.md`) to remove WhatsApp from active big-plan critical path and reframe it as an optional legacy adapter.
- 2026-04-24 08-41-46 Updated AI runtime defaults in `src/agents/dispatcher.py` and `.env.example` to Gemini-first (`AGENT_PROVIDER=gemini`, `GEMINI_API_KEY`, `GEMINI_MODEL`), while preserving OpenAI/Anthropic as optional fallback providers.
- 2026-04-23 13-38-36 **PRODUCTION DEPLOYMENT CONFIRMED LIVE:** Brain is running on Railway at `https://solo-leveling-production-36c8.up.railway.app`. All server connectivity tests pass; webhook endpoint active with security validation; ready for WhatsApp integration testing.

### Removed

- 2026-04-24 08-56-31 Deleted the entire WhatsApp integration module (`src/integrations/whatsapp/`) and removed WhatsApp-specific scheduler/config dependencies to align code with approved API/CLI-first architecture.
- 2026-04-24 08-56-31 Removed `twilio`, `openai`, and `anthropic` from `requirements.txt` after provider and channel deprecation.

- 2026-04-23 13-29-58 Added `docs/RAILWAY_DEPLOYMENT_WORKFLOW.md`: end-to-end deployment guide from local validation through Railway live health verification; 6-phase workflow (Pre-deployment, Deploy, Health verify, Persistence volumes, Meta webhook, Staging setup) with step-by-step instructions, curl examples, WhatsApp testing commands, and troubleshooting matrix. Enables operators to go from code → deployed + live + verified in ~30-45 minutes.
- 2026-04-23 13-26-46 Added `docs/RAILWAY_HEALTH_VERIFICATION.md`: comprehensive health check guide covering local testing via Python, FastAPI endpoint validation, integration status breakdown (critical vs. optional), pre-Railway checklist, post-Railway WhatsApp testing, troubleshooting matrix, and reference to health handler source code. Enables operators to validate environment variables and credential setup before and after Railway deployment.
- 2026-04-23 13-25-11 Added `docs/DEPLOYMENT_STATUS.md`: comprehensive Railway deployment checklist covering repository readiness, 7-phase setup sequence (project setup, env vars, first deploy, verification, Meta webhook, volumes, operations), credential inventory, and staging/prod decision rationale. Links all relevant runbooks and governance docs for operator clarity.
- 2026-04-23 13-23-12 Added lightweight "Release Checklist" section to `docs/ai-team-coordination.md` to gate `development` → `main` releases with actionable pre-merge criteria (tests passing, changelog updated, docs current, no regressions, clean branch, CI validated) and release PR format guidance.
- 2026-04-23 13-19-29 Added remote `development` branch as the shared staging/integration branch. Team flow is now explicit: `main` for production release, `development` for integration, and `agent/lead/program` branches for scoped implementation.
- 2026-04-23 12-58-55 Added inline Google credential support for Railway-style env vars: Drive now accepts `GOOGLE_DRIVE_CREDENTIALS_JSON` (with `GOOGLE_CREDENTIALS_JSON` legacy fallback), and Gmail now accepts `GMAIL_CREDENTIALS_JSON` (with `GOOGLE_CREDENTIALS_JSON` legacy fallback). Path-based variables remain supported.
- 2026-04-23 12-58-55 Added inline-credential regression tests in `tests/test_integration_smoke.py` (`InlineCredentialSupportTests`) to validate Drive/Gmail JSON env loading paths without file mounts.
- 2026-04-23 11-02-18 Added GMAIL_ENABLED feature flag: set to false in .env disables all Gmail routes with an informative message without removing credentials. Guard wired in router, workflow detection, and health check. Dotenv bootstrapped in config.py and handler.py. All 35 tests pass.
- 2026-04-23 11-02-18 Added docs/research/railway-setup-runbook-2026-04-23.md: 7-part Railway deployment guide covering GitHub connection, env var setup, credential JSON strategy, Meta webhook registration, volume persistence, operations checklist, and key gotchas.
- 2026-04-23 11-02-18 Added docs/research/payment-method-indonesia-2026-04-23.md: virtual card and no-CC options for Indonesia including Jenius e-Card (recommended), Jago, Wise, Revolut, and Railway free-credit workaround. Estimated monthly cost ~5-10 USD.
- 2026-04-23 10-33-27 Added durable research outputs under `docs/research/`: `ai-key-providers-2026-04-23.md` (20 AI key providers with tiering, suitability, and key setup instructions) and `deployment-hosting-2026-04-23.md` (20 hosting options with tiering, setup guides, Mac mini M4 hosting viability, and domain strategy analysis).
- 2026-04-23 10-33-27 Added decision record `docs/decisions/004-research-recording-and-approval-gate.md` to formalize explicit owner approval before policy execution and mandatory durable research recording.
- 2026-04-22 12-02-12 Added separate Google credential env support: `GOOGLE_DRIVE_CREDENTIALS_PATH` for Drive service-account auth and `GMAIL_CREDENTIALS_PATH` for Gmail OAuth auth, while keeping `GOOGLE_CREDENTIALS_PATH` as a backward-compatible fallback.
- 2026-04-22 12-02-12 Added smoke/test coverage and docs updates for the split Google credential model; current live validation confirms Notion credentials work with the active `.env`.
- 2026-04-22 11-28-51 Added provider-aware health validation in router so WhatsApp checks now follow `WHATSAPP_PROVIDER`: Meta requires `META_ACCESS_TOKEN`, `META_VERIFY_TOKEN`, `META_PHONE_NUMBER_ID`; Twilio requires `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER`.
- 2026-04-22 11-28-51 Added router smoke coverage for health command provider behavior in `tests/test_integration_smoke.py` (`test_route_health_smoke_meta_provider` and missing-meta-phone-id guard).
- 2026-04-22 11-14-57 Added first filled operational governance records: `docs/task-cards/MULTI-AI-004-weekly-performance-kickoff-2026-04-22.md` and `docs/scorecards/weekly-rl-okr-scorecard-2026-W17-main-brain.md`, enabling immediate weekly owner evaluation and non-template task tracking.
- 2026-04-22 11-09-04 Added `docs/templates/weekly-rl-okr-scorecard-example-2026-W17.md`, a prefilled weekly scorecard example based on current documented team/project state so scoring can start immediately with no manual setup.
- 2026-04-22 11-00-50 Added `docs/templates/task-card-template.md` and `docs/templates/weekly-rl-okr-scorecard-template.md` as ready-to-use execution templates for task assignment, validation handoff, weekly RL testing, OKR tracking, and owner self-review.
- 2026-04-22 10-51-38 Added `docs/ai-employer-operating-system.md` as the canonical AI employer policy covering role-branch-authority governance, unified task schema, RL1-RL5 responsibility levels, OKR scoring formulas, responsibility-level testing thresholds, and revenue-impact assignment rules.
- 2026-04-22 10-51-38 Added `docs/decisions/003-ai-employer-governance-model.md` to formalize adoption of the new governance and valuation model.
- 2026-04-22 10-14-03 Added `health` command to router — reports ✅/❌ per integration based on env var presence. Accessible via WhatsApp or any interface using trigger words: "health", "check setup", "system health", "integration status".
- 2026-04-22 10-14-03 Added handoff secret→test mapping table and live smoke test guide to `docs/SETUP_SECRETS.md` so any new device or AI session can verify credentials end-to-end in one command.
- 2026-04-22 10-14-03 Added master `ENABLE_LIVE_SMOKE_TESTS=1` env toggle to `tests/test_integration_smoke.py` that gates all three live integration tests as a group, replacing the previous per-test credential checks at the class level.
- 2026-04-22 10-14-03 Added 10 new Stage 9 library test cases covering larger corpus search, empty query, no-match queries, deep-capture edge inputs, sensitive data rejection, sequential index rebuilds, bundle lookup, and summary extraction.
- 2026-04-22 10-14-03 Added `_startup_checks()` to `src/integrations/whatsapp/handler.py` — auto-creates `library/` and `data/` mount dirs on startup and logs warnings for any unconfigured optional credential env vars.
- 2026-04-22 10-14-03 Added Runbook section to `README.md` with local dev commands, container run recipe with expected log output, health check commands, container restart behavior, credential setup, and single-group test run commands.

### Fixed

- 2026-04-22 12-32-09 Fixed integration tests not loading `.env` file automatically. Added `dotenv.load_dotenv()` call at module level in `tests/test_integration_smoke.py` so all three live smoke tests (Drive, Gmail, Notion) now execute correctly without requiring explicit environment variable passing. All 3 tests now pass: Drive ✅, Gmail ✅, Notion ✅.

### Changed

- 2026-04-23 13-19-29 Updated `.github/workflows/ci.yml` to run on both `development` and `main` for pushes and pull requests, enabling CI coverage for staging before production release.
- 2026-04-23 12-58-55 Removed Dockerfile `VOLUME` directive because Railway bans the `VOLUME` keyword; persistence is now expected to be configured in Railway Volumes at deploy time.
- 2026-04-22 10-14-03 Rewrote `src/core/scheduler.py` module docstring to document container restart behavior: reminders persist via `data/` volume mount, jobs always re-register on startup, overdue reminders fire on first scheduler tick.

### Docs

- 2026-04-23 17-20-45 Added lightweight versioned release-section template in `CHANGELOG.md` so each new main-branch tag can publish consistent release notes (`## [vX.Y.Z] - YYYY-MM-DD`) without changing original entry timestamps.
- 2026-04-23 17-06-51 Updated `docs/ai-team-coordination.md` and `docs/ai-knowledge/conventions.md` to formalize semantic git tag versioning on `main` releases (`vMAJOR.MINOR.PATCH`), including release-gate checks, tag creation commands, and bump rules.
- 2026-04-23 14-56-07 Updated `AI_INSTALLATION.md` with researched change-record guidance for multi-AI workflows: recommends layered record model (git commits + curated changelog + continuity notes + decisions), plus explicit read-before-work and write-after-work protocol for consistent cross-AI collaboration.
- 2026-04-23 13-19-29 Updated `docs/ai-employer-operating-system.md` and `docs/ai-team-coordination.md` to formalize branching policy: `main` as production (release-only), `development` as staging/integration, and release flow `agent/lead/program -> development -> main`.
- 2026-04-23 12-58-55 Updated `docs/research/railway-setup-runbook-2026-04-23.md` to reflect that inline JSON credential env vars are now implemented (no extra code session required).
- 2026-04-23 10-47-47 Added Railway Acceptable Use Policy compliance review to `docs/research/deployment-hosting-2026-04-23.md`: confirmed project use of official Meta Cloud API webhook is not a userbot violation; includes per-dimension compliance table and ongoing Gmail OAuth scope obligation.
- 2026-04-23 10-43-09 Expanded `docs/research/deployment-hosting-2026-04-23.md` with an execution-level Railway/Fly.io deep dive: detailed setup flows, architecture notes, side-by-side comparison matrix, and immediate decision guidance for deployment-day selection.
- 2026-04-23 10-33-27 Updated `AGENTS.md` and `.github/copilot-instructions.md` with explicit approval-gate rules for policy/process updates and mandatory `docs/research/` recording for substantial research outputs.
- 2026-04-23 10-33-27 Updated `docs/README.md` and `docs/ai-working-notes.md` to register the new research records and governance decision for cross-session continuity.
- 2026-04-22 11-28-51 Updated `docs/SETUP_SECRETS.md` secret-to-test mapping for provider-specific WhatsApp credentials so `health` output aligns with actual Meta/Twilio runtime env keys.
- 2026-04-22 11-14-57 Updated `docs/README.md`, `docs/ai-working-notes.md`, and `docs/ai-knowledge/continuation-plan.md` to define canonical storage paths for filled records: `docs/task-cards/` and `docs/scorecards/`.
- 2026-04-22 11-09-04 Updated `docs/README.md`, `docs/ai-working-notes.md`, and `docs/ai-knowledge/continuation-plan.md` to register the new prefilled weekly scorecard example in the standard workflow.
- 2026-04-22 11-00-50 Updated `docs/ai-employer-operating-system.md` to include Main Brain self-performance scoring (`Owner_cycle`) and self-management measurement criteria in weekly evaluation.
- 2026-04-22 11-00-50 Updated `docs/README.md`, `docs/ai-working-notes.md`, and `docs/ai-knowledge/continuation-plan.md` to register and operationalize the new templates and owner self-review workflow.
- 2026-04-22 10-51-38 Updated `docs/ai-team-coordination.md` to operationalize the new governance model and clarify branch flow, escalation, and monitor checklist.
- 2026-04-22 10-51-38 Updated `docs/README.md`, `AI_CONTEXT.md`, and `docs/ai-working-notes.md` so discoverability, active priorities, and cross-session memory reflect the new employer/OKR system.
- 2026-04-22 10-14-03 `docs/SETUP_SECRETS.md` — extended Done checklist with `health` command verification step and added secret→test mapping table plus live smoke test invocation examples.

 capturing this session's WhatsApp setup guidance, Meta legal-verification research conclusions, and the API-setup UI troubleshooting notes for later review.
- 2026-04-22 09-54-38 Added `docs/PLAN-WITHOUT-WHATSAPP-2026-04-22.md` with a phased execution plan to keep project progress moving while WhatsApp integration is intentionally paused.
- 2026-04-21 21-52-07 Added `.github/workflows/ci.yml` GitHub Actions pipeline that runs all 23 tests on every push and pull request to `main`. Credential-gated live tests are automatically skipped in CI (no secrets needed). Establishes a continuous safety net for regression detection without manual test runs.
- 2026-04-21 21-52-07 Added `docs/TASK-MULTI-AI-003.md` defining the CI pipeline setup task with acceptance criteria, scope, and execution plan.
- 2026-04-21 19-30-19 Added `tests/test_integration_smoke.py` as a credential-aware integration smoke suite with router mocks, workflow and AI guardrails, optional live Notion/Drive/Gmail checks, and explicit skip messaging for missing credentials.

### Decisions

- 2026-04-23 17-06-51 Adopted semantic git-tag release policy for `main` (`vMAJOR.MINOR.PATCH`) with annotated tags pushed after `development -> main` release merges; decision record: `docs/decisions/005-main-branch-semver-tagging.md`.
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
