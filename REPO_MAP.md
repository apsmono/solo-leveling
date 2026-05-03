# Repo Map

A navigational guide to every significant area of the repository. Read this to find where things live before you edit.

---

## Top-Level Files

| File | Purpose | Read Before Editing |
|------|---------|---------------------|
| `README.md` | Mission, runbook, container instructions | Always |
| `CLAUDE.md` | AI onboarding hub connecting all docs | First file for AI assistants |
| `AGENTS.md` | Mandatory AI agent rules and changelog standard | Every session |
| `AI_CONTEXT.md` | Current phase, active priorities, completed stages | Every session |
| `CONVENTIONS.md` | Git, code, documentation, and testing conventions | When unsure about style |
| `GLOSSARY.md` | Project-specific terminology | When you encounter an unfamiliar term |
| `ARCHITECTURE.md` | High-level system architecture overview | Before structural changes |
| `CHANGELOG.md` | Human-readable change history | After making notable changes |
| `AI_INSTALLATION.md` | Reusable bootstrap guide for other repos | When setting up a new repo |
| `requirements.txt` | Python dependencies | When adding packages |
| `Dockerfile` | Container build definition | When changing runtime |
| `.env.example` | Environment variable template | When adding new config |

---

## `src/` — Application Code

### `src/app.py`
FastAPI entry point. Defines the lifespan manager (startup checks + scheduler), `/healthz`, and `/command` endpoints.

**Before editing:** understand the scheduler lifecycle in `src/core/scheduler.py`.

### `src/core/` — Brain Core

| File | Responsibility | Key Symbols |
|------|---------------|-------------|
| `router.py` | Intent detection and command dispatch | `INTENT_MAP`, `route_command()`, `_dispatch()` |
| `workflows.py` | Multi-step workflow chains | `handle_workflow_command()`, `_workflow_inbox_summary_to_notion()` |
| `scheduler.py` | Reminders, digests, cron jobs | `start_scheduler()`, `process_due_reminders()` |
| `libraries.py` | Personal knowledge library (Stage 9) | `handle_library_command()`, `SearchCache`, `_capture_research_bundle()` |
| `config.py` | Environment variable loader | `require()`, `_get_bool()`, `_get_int()` |

**Before editing `router.py`:** adding a command requires updating `INTENT_MAP`, adding a handler, and wiring it into `_dispatch()`.

**Before editing `libraries.py`:** this is the largest module (~1,100 lines). Changes affect `library/` file structure, `library/index.json`, and the search cache.

### `src/agents/` — AI Orchestration

| File | Responsibility | Key Symbols |
|------|---------------|-------------|
| `dispatcher.py` | Gemini API client wrapper | `run_agent()`, `_run_gemini()` |

**Before editing:** changes here affect every AI-powered feature (library capture, ask AI, workflow summarization).

### `src/integrations/` — External Services

| Directory | Service | Auth Method | Key File |
|-----------|---------|-------------|----------|
| `notion/` | Notion API | Integration token | `client.py` — search, get_page, create_page, query_database |
| `gdrive/` | Google Drive API | Service account | `client.py` — list_files, read_doc, create_doc, move_file |
| `gmail/` | Gmail API | OAuth2 | `client.py` — list_unread, search_messages, get_message, inbox_summary |

**Before editing any integration:** read `docs/architecture/integrations.md` for the contract and security rules.

---

## `tests/` — Validation

| File | Coverage |
|------|----------|
| `test_integration_smoke.py` | Router smoke tests, inline credential tests, optional live integration tests |
| `test_stage9_libraries.py` | Library system: capture, search, cache, bundles, maintenance, malformed input |

**Run before committing:** `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v`

---

## `docs/` — Documentation

### `docs/architecture/`
- `command-center.md` — Full system architecture with layered diagram, data flow, stage table
- `integrations.md` — Per-service contracts: Notion, Drive, Gmail, Gemini, Notifications

### `docs/decisions/`
Numbered formal decision records (001–006). Use `docs/decision-log-template.md` for new ones.

### `docs/ai-knowledge/`
Cross-session AI memory split by topic:
- `build-history.md` — stage-by-stage construction log
- `conventions.md` — changelog and git workflow rules
- `error-log.md` — errors with root cause and prevention
- `integration-patterns.md` — per-service gotchas
- `security-rules.md` — non-negotiable constraints
- `continuation-plan.md` — what is done, what is next

**Entry point:** `docs/ai-working-notes.md` links to all of the above.

### `docs/research/`
Durable research outputs dated `YYYY-MM-DD`: deployment hosting, AI providers, Railway runbook, payment methods, deployable AI context.

### `docs/templates/`
Reusable execution templates: task card, weekly scorecard template, scorecard example.

### `docs/task-cards/` and `docs/scorecards/`
Filled operational records for completed work.

### `docs/` Root-Level Strategy Files
- `self-development-system.md` — personal growth operating model
- `financial-freedom-strategy.md` — wealth-building system
- `habit-system.md` — recurring behaviors and anti-habits
- `review-rhythm.md` — daily/weekly/monthly/quarterly cadence
- `personal-knowledge-system-design.md` — Stage 9 research and implementation plan
- `personal-library-formatting-guide.md` — 300+ line formatting standard
- `ai-employer-operating-system.md` — governance, roles, RL levels, OKR scoring
- `ai-team-coordination.md` — operational coordination and branch workflow

---

## `subprojects/` — Monorepo Projects

Static sites and microservices housed in the same repo for discoverability.

| Directory | Contents | Deploy Target |
|-----------|----------|---------------|
| `wedding-invitation/` | Wedding invitation static site (HTML/CSS/JS) | Cloudflare Pages |
| `koperasi-landing/` | Koperasi KKS landing page static site (HTML/CSS/JS) | Cloudflare Pages |
| `scrapers/` | Python scraping scripts | Local / scheduled |
| `microservices/` | Standalone FastAPI services | Docker / MacMini |

---

## `library/` — Knowledge Storage

The filesystem-based personal library. All content is markdown with YAML frontmatter.

```
library/
  index.json          # Generated catalog of all entries and bundles
  profile/            # Skills, interests, domains, learning priorities
  terms/              # Definitions and concepts
  books/              # Reading list and book notes
  articles/           # Article captures
  thoughts/           # Draft ideas and reasoning
  references/         # Reference materials
  research/           # Deep research bundles (directories)
```

**Important:** this directory is mounted as a Docker volume. Do not delete it.

---

## `data/` — Runtime State

- `reminders.json` — Persistent reminder store for the scheduler

**Important:** this directory is mounted as a Docker volume. Do not delete it.

---

## `prompts/` — Reusable AI Prompts

Stored prompt templates used by the owner or AI tools. Cross-device startup prompts live here.

---

## `scripts/` — Automation Scripts

Utility scripts such as `device-sync.sh` for cross-device continuity.

---

## `config/` — Configuration Templates

Zsh and shell configuration templates. Not runtime configuration (that lives in `.env`).
