# AI Context

## Project Intent

This repository is the central brain for the owner's personal operating system: self-development, financial freedom, and full automation of connected tools. It holds persistent context and decisions, routes commands from automation interfaces, integrates with Notion, Google Drive, and Gmail, and orchestrates AI agents for complex tasks.

## Current Phase

- Phase: Stage 8 complete; Stage 9 in progress; Firebase/Telegram/Dashboard infrastructure landed
- Main assets: working integration code (Notion, Drive, Gmail, Gemini), notification scheduler with Firestore/JSON dual backend, Stage 8 workflow set, Stage 9 library handlers, local `library/` folder structure, generated `library/index.json`, comprehensive formatting standard, deep research-bundle capture flow, indexed search with LRU cache, Firebase Auth + Firestore integration, Telegram bot webhook, static dashboard frontend for GitHub Pages under `subprojects/dashboard`, versioned REST API (`/api/v1`), Docker Compose for MacMini, monorepo `subprojects/` scaffolding with auto-sync to external repos
- Current work: backend runs on MacMini via Docker; static dashboard deploys to GitHub Pages from `subprojects/dashboard`; Telegram and HTTP `/command` both route through `route_command()`; Firestore stores reminders and command history when `USE_FIRESTORE_REMINDERS=true`; single-user Firebase Auth gates `/dashboard` endpoints; static-site sub-projects (`dashboard`, `wedding-invitation`, `koperasi-landing`) auto-sync to standalone repos on every push to `main`
- Primary need: configure Firebase credentials and `FRONTEND_ORIGIN`, deploy dashboard to GitHub Pages, set Telegram webhook via `scripts/set-telegram-webhook.py`, verify end-to-end auth flow, then continue Stage 9 improvements
- Device note: owner switches between devices frequently; treat `docs/ai-working-notes.md` as the cross-session memory

## Source Of Truth

- `README.md` describes the repository mission and structure at a high level.
- `AGENTS.md` defines repository-wide agent expectations and changelog rules.
- `.github/copilot-instructions.md` defines GitHub Copilot behavior for this repo.
- `CHANGELOG.md` records notable project changes in human-readable form.
- `docs/AI_CHANGELOG_POLICY.md` defines the changelog format and maintenance standard.
- `docs/README.md` maps all planning documents and architecture references.
- `docs/architecture/command-center.md` is the canonical architecture document.
- `docs/architecture/integrations.md` defines all integration contracts.
- `docs/decisions/` holds formal decision records for all major choices.
- `AI_INSTALLATION.md` explains how to reproduce this setup elsewhere.

## Growth Conventions

As the project expands, prefer this structure:

- `docs/` for strategy documents, plans, decision logs, and reference material
- `docs/architecture/` for system design and integration specifications
- `docs/decisions/` for formal decision records (numbered sequentially)
- `prompts/` for reusable AI prompts
- `src/` for integration connectors, command handlers, and automation scripts
- `src/integrations/` for one subfolder per external service
- `tests/` for validation once executable logic exists

## AI Collaboration Rules

- Keep AI-facing instructions synchronized with the actual repository structure.
- When adding a new subsystem, document its purpose, entry points, and maintenance expectations.
- Prefer explicit templates, checklists, and decision logs over vague narrative notes.
- If commands, environments, or dependencies are introduced, document setup and verification steps immediately.
- For notable changes, update `CHANGELOG.md` using the local-device timestamp format `YYYY-MM-DD HH-mm-ss`. Get the timestamp with: `date "+%Y-%m-%d %H-%M-%S"`
- When a change alters intent, usage, workflow, or structure, update the related documentation and short descriptions in the same change.
- **After every session, write your findings back to `docs/ai-working-notes.md` and update this file if priorities or completed stages have changed.** This repo is the only shared memory between devices and AI collaborators.

## Current Priorities

1. ~~Expand Stage 8 from starter workflow to multiple robust workflow chains~~ **DONE (3 workflows implemented)**
2. **ACTIVE: Deploy and verify Firebase + Dashboard + Telegram end-to-end** — configure Firebase credentials, deploy `subprojects/dashboard/` to GitHub Pages, set Telegram webhook, verify auth flow and CORS
3. ~~Implement Stage 9 — Personal Knowledge Libraries command layer~~ **DONE** (`library/` folder is canonical storage; all handlers are local-library-first)
4. **ACTIVE: Multi-AI Team Execution** — governance upgraded with role-branch-authority policy, responsibility-level testing, and OKR valuation in `docs/ai-employer-operating-system.md`; upcoming coordinated tasks must use this model.
5. **ACTIVE: Autopilot System** — Phase 1 MVP live in `src/autopilot/`. RL-governed autonomous loop with Kimi API via litellm. Commands: `autopilot start: <goal>`, `autopilot status`, `autopilot pause`, `autopilot approve`. Phase 2 will add Claude Code subprocess client, write tools, and approval queue.
6. **ACTIVE: Sub-project Deployment** — `subprojects/wedding-invitation/` and `subprojects/koperasi-landing/` are scaffolded and ready for Cloudflare Pages deployment. Next: customize content, connect to Cloudflare Dashboard, and deploy to `*.pages.dev`.
7. ~~Choose a deployment target~~ **DONE** — MacMini (backend via Docker Compose) + GitHub Pages (static dashboard frontend)
8. **NEW: Deploy static sub-projects** — `subprojects/wedding-invitation/` and `subprojects/koperasi-landing/` to Cloudflare Pages.
6. ~~Add tests with at least one integration smoke test per service~~ **DONE** — 59 tests (Firebase auth, Firestore, dashboard API, Telegram webhook, Stage 9 libraries, integration smoke)

## Completed Stages

| Stage | What                                                              | Status          |
| ----- | ----------------------------------------------------------------- | --------------- |
| 1     | Foundation — scaffold, docs, changelog policy                     | Done            |
| 2     | Command interface baseline (API/CLI command server)                | Done            |
| 3     | Notion — search, read, create page, query database                | Done            |
| 4     | Google Drive — list, read (export), create doc, move              | Done            |
| 5     | Gmail — list unread, search, read message, inbox summary (OAuth2) | Done            |
| 6     | Notifications — proactive push scheduler                          | Done            |
| 7     | AI agent orchestration — Gemini dispatcher                          | Done            |
| 8     | Multi-step workflows — chained command handler                    | Done            |
| 9     | Personal Knowledge Libraries                                      | **In progress** |

## Active Planning Documents

- `docs/architecture/command-center.md` — full system architecture, stage table, data flow.
- `docs/architecture/integrations.md` — integration contracts and current status per service.
- `docs/decisions/` — formal decision records (001: command-center scope, 002: WhatsApp approach, 006: interface and Gemini provider pivot).
- `docs/ai-working-notes.md` — **AI cross-session memory**: build history, error log, integration patterns, security rules, continuation plan. Read this. Update this after every session.
- `docs/self-development-system.md` — personal growth and execution design (placeholder, needs real data).
- `docs/financial-freedom-strategy.md` for income, assets, leverage, and risk planning.
- `docs/habit-system.md` for repeatable daily and weekly behavior design.
- `docs/review-rhythm.md` for daily, weekly, monthly, and quarterly review loops.
- `docs/decision-log-template.md` for the reusable decision record template.
