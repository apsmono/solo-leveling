# CLAUDE.md — AI Onboarding Hub

This is the single entry point for AI assistants working in the solo-leveling repository. Read this file first, then follow the links to deeper documentation.

---

## Start Here

**solo-leveling** is a personal command-center brain built with FastAPI. It receives text commands via HTTP, detects intent, and dispatches to handlers that integrate with Notion, Google Drive, Gmail, and Gemini AI. It also manages a filesystem-based personal knowledge library under `library/`.

---

## Read This First

Read these files in order before doing any work:

1. **[README.md](README.md)** — Mission, runbook, container instructions, and quickstart
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** — High-level system architecture, data flows, key modules, technology stack
3. **[CONVENTIONS.md](CONVENTIONS.md)** — Git workflow, Python code style, documentation rules, testing conventions
4. **[REPO_MAP.md](REPO_MAP.md)** — Where every file lives and what it does
5. **[GLOSSARY.md](GLOSSARY.md)** — Definitions for project-specific terms (stages, bundles, RL levels, etc.)

Then read the operational files:

6. **[AGENTS.md](AGENTS.md)** — Mandatory AI agent rules, read/write protocol, changelog rules, approval gate
7. **[AI_CONTEXT.md](AI_CONTEXT.md)** — Current phase, active priorities, completed stages, source-of-truth index

---

## Before You Edit

- [ ] Read `AI_CONTEXT.md` to confirm the current phase and priorities
- [ ] Read `AGENTS.md` for the read-before-work / write-after-work protocol
- [ ] Run `git fetch --all --prune && git status -sb`
- [ ] If behind, run `git pull --ff-only`
- [ ] Check `REPO_MAP.md` to locate the files you need to change
- [ ] Run tests: `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v`
- [ ] Ensure tests pass before you start editing

---

## Where Things Live

| What | Where | Quick Link |
|------|-------|------------|
| AI onboarding hub | Root | You are here |
| Runbook + quickstart | Root | [README.md](README.md) |
| Architecture overview | Root | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Deep architecture | `docs/architecture/` | `command-center.md`, `integrations.md` |
| Conventions | Root | [CONVENTIONS.md](CONVENTIONS.md) |
| Repo navigation | Root | [REPO_MAP.md](REPO_MAP.md) |
| Terminology | Root | [GLOSSARY.md](GLOSSARY.md) |
| Agent rules | Root | [AGENTS.md](AGENTS.md) |
| Current phase / priorities | Root | [AI_CONTEXT.md](AI_CONTEXT.md) |
| Decision records | `docs/decisions/` | `001-command-center-scope.md` through `006-interface-and-gemini-pivot.md` |
| AI cross-session memory | `docs/ai-knowledge/` | `build-history.md`, `error-log.md`, `continuation-plan.md` |
| Application code | `src/` | `app.py`, `core/`, `agents/`, `integrations/` |
| Tests | `tests/` | `test_integration_smoke.py`, `test_stage9_libraries.py` |
| Knowledge storage | `library/` | Markdown files organized by section |
| Runtime state | `data/` | `reminders.json` |

---

## How We Work

### Git
- Branch naming: `agent/<name>/<slug>/<scope>` for features, `lead/<reviewer>/<slug>` for review, `program/<milestone>` for milestones
- Before edits: `git fetch --all --prune && git status -sb`
- After any pull/push: re-read `AI_CONTEXT.md` and `docs/ai-knowledge/continuation-plan.md`
- Post-edit: commit, then push. Prefer PRs to `main`.

### Code
- Absolute imports with `src.` prefix. No relative imports.
- Use `from __future__ import annotations`.
- Private helpers prefixed with `_`.
- Catch `EnvironmentError` separately in handlers; log unexpected exceptions with `logger.exception()`.

### Docs
- Update docs in the same change when behavior, structure, or env vars change.
- Timestamp format: `YYYY-MM-DD HH-mm-ss`.
- Changelog: `CHANGELOG.md`, reverse chronological, grouped by `Added/Changed/Fixed/Removed/Docs/Decisions`.

Full details: [CONVENTIONS.md](CONVENTIONS.md)

---

## Key Terms

| Term | Meaning |
|------|---------|
| **Brain** | The command-center core (`src/core/router.py`) |
| **Intent Map** | Keyword-to-handler mapping in `router.py` |
| **Stage 9** | Personal Knowledge Libraries — the active development phase |
| **Research Bundle** | A directory of 7 markdown files created during deep capture |
| **Deep Capture** | The AI-assisted "add to library" flow |
| **RL Level** | Responsibility Level (RL1–RL5) defining AI autonomy |
| **Task Card** | Structured task definition using the template in `docs/templates/` |
| **Workflow** | Multi-step command chaining integrations |

Full definitions: [GLOSSARY.md](GLOSSARY.md)

---

## Architecture at a Glance

```
HTTP POST /command  →  FastAPI  →  Router  →  Handler
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
               Integrations         AI Agent (Gemini)      Scheduler
               (Notion, Drive,                         (Reminders, digests)
                Gmail)
```

Three main flows:
1. **Inbound command** — text → intent detection → handler → reply
2. **Library deep capture** — AI analysis → research bundle + supporting entries → index rebuild
3. **Workflow execution** — chain integration calls (e.g., Gmail → Notion)

Full details: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Decision Records

Major architectural and policy decisions are recorded in `docs/decisions/`:

- `001-command-center-scope.md` — Redefine repo as central brain
- `002-whatsapp-approach.md` — WhatsApp provider choice
- `003-ai-employer-governance-model.md` — Role-branch-authority governance
- `004-research-recording-and-approval-gate.md` — Approval gate protocol
- `005-main-branch-semver-tagging.md` — Semantic versioning on `main`
- `006-interface-and-gemini-pivot.md` — Gemini as primary AI, WhatsApp deprioritized

Create a new decision record using `docs/decision-log-template.md` when making significant scope, structure, or policy choices.

---

## Current Phase

See **[AI_CONTEXT.md](AI_CONTEXT.md)** for:
- Current phase and active priorities
- Completed stages table (Stages 1–8 done, Stage 9 in progress)
- Active planning documents
- Source-of-truth file index

---

## After You Finish

**Mandatory write-back checklist:**

- [ ] Update `docs/ai-working-notes.md` (or the relevant `docs/ai-knowledge/` file) with patterns, errors, or decisions discovered
- [ ] Update `AI_CONTEXT.md` if the current phase, completed stages, or active priorities have changed
- [ ] Update `CHANGELOG.md` with all notable changes using timestamp `YYYY-MM-DD HH-mm-ss`
- [ ] Create a `docs/decisions/NNN-*.md` if any significant architectural or policy choice was made
- [ ] Run tests: `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v`
- [ ] Commit and push: `git push`

> Think of it this way: when you finish, the next AI that opens this repo should be able to read the docs and know exactly what you did, what you found, and where to continue — without needing to re-explore the codebase.

---

## Quick Links

- [README.md](README.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [CONVENTIONS.md](CONVENTIONS.md)
- [REPO_MAP.md](REPO_MAP.md)
- [GLOSSARY.md](GLOSSARY.md)
- [AGENTS.md](AGENTS.md)
- [AI_CONTEXT.md](AI_CONTEXT.md)
- [CHANGELOG.md](CHANGELOG.md)
