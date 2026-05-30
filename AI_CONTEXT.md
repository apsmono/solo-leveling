# AI Context

## Project Intent

This repository is the central brain for the owner's personal operating system: self-development, financial freedom, and full automation of connected tools. It holds persistent context and decisions, routes commands from automation interfaces, integrates with Notion, Google Drive, and Gmail, and orchestrates AI agents for complex tasks.

## Current Phase

- Phase: **Phase 2 (Signal n8n Execution Layer) complete** and **Phase 3 (Signal Knowledge Library + Conceptual Search + AI Guide) complete** — ready for Phase 4 (Zen Shell + Clarity Board)
- Main assets: working integration code (Notion, Drive, Gmail, Gemini), notification scheduler with Firestore/JSON dual backend, Stage 8 workflow set, Stage 9 library handlers, local `library/` folder structure, generated `library/index.json`, comprehensive formatting standard, deep research-bundle capture flow, indexed search with LRU cache, Firebase Auth + Firestore integration, **Telegram bot webhook with proactive messaging + CLI management**, static dashboard frontend for GitHub Pages (standalone repo), versioned REST API (`/api/v1`), Docker Compose for MacMini, **pgvector vector spine (`src/vector/`) with Gemini embeddings, token cache, and automatic library indexing**, **Firebase session cookie auth (`/auth/session-login`, `/auth/session-logout`) with httpOnly Secure SameSite=Strict cookies**, **conceptual vector search (`src/vector/search.py`) with keyword/vector/hybrid modes**, **LLM intent parser (`src/core/intent_parser.py`) driving `route_command`**, **AI Guide REST API (`src/api/guide.py`)**, **dashboard AI Guide panel (persistent right-hand Command Bar + Status Banner + Distraction Gate)**, **n8n execution layer (`src/n8n/`): Public REST client, soft error abstraction, versioned workflow template skeletons, owner-credential injection, intent executor with LLM parameter fill + RL approval gate, and the `POST /api/v1/webhook/n8n` execution callback endpoint**
- Current work: Phase 4 — Zen Shell + Clarity Board (70/30 split-screen, migrate Guide panel into locked Panel B)
- Primary need: Build the Zen workspace shell around the Phase 3 Knowledge Library and AI Guide surfaces
- n8n note: workflow template JSONs ship with `n8n_workflow_id: 0` placeholders — a live n8n instance must be provisioned and the real workflow IDs recorded (manual checkpoint, plan 02-03 Task 3) before end-to-end triggering works. Config: `N8N_BASE_URL`, `N8N_API_KEY` (generate in n8n UI → Settings → API).
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

1. **ACTIVE: Phase 4 — Zen Shell + Clarity Board** — 70/30 split-screen workspace; migrate AI Guide panel into locked Panel B; Core Dashboard focus block + Context Nest
2. ~~**Phase 3 — Knowledge Library + Conceptual Search + AI Guide**~~ **DONE** — vector search, LLM intent parser, Guide API, dashboard AI Guide panel
3. ~~**Phase 1 — Signal Data & Auth Foundation**~~ **DONE** — vector spine + persistent Google OAuth session cookies
4. ~~Expand Stage 8 from starter workflow to multiple robust workflow chains~~ **DONE (3 workflows implemented)**
5. ~~Implement Stage 9 — Personal Knowledge Libraries command layer~~ **DONE** (`library/` folder is canonical storage; all handlers are local-library-first)

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
- `docs/self-development-system.md` — personal growth and execution design (filled: capability areas, identity targets, failure patterns).
- `docs/financial-freedom-strategy.md` — income, assets, leverage, and risk planning (filled: strategy pillars, income engine, guardrails).
- `docs/habit-system.md` — repeatable daily and weekly behavior design (filled: active habits, anti-habits, friction design).
- `docs/review-rhythm.md` — daily, weekly, monthly, and quarterly review loops (filled: cadence, questions, automation).
- `docs/decision-log-template.md` for the reusable decision record template.
