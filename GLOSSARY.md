# Glossary

Definitions for terms used across the codebase, documentation, and AI collaboration context.

---

## System Terms

**Brain**
The command-center core that receives text commands, detects intent, and dispatches to handlers. Lives in `src/core/router.py` and `src/core/workflows.py`.

**Command Center**
The overall system architecture: FastAPI server + brain core + integrations + AI agents + scheduler.

**Intent Map**
The keyword-to-handler mapping in `src/core/router.py`. Each intent (e.g., `library_capture`, `gmail_summary`) has a list of trigger keywords. See `INTENT_MAP`.

**Intent Detection**
The process of converting free-form text into a known intent key. Compound workflow detection runs before the keyword map (e.g., "summarise inbox and save to notion").

**Handler**
A function that executes a specific intent. All handlers are wrapped in `try/except` inside `_dispatch()`.

---

## Stage Terms

The project is built in numbered stages. Each stage adds a major capability.

| Stage | Name | Key File |
|-------|------|----------|
| 1 | Foundation | scaffold, docs, changelog policy |
| 2 | Command Interface | `src/app.py`, `src/core/router.py` |
| 3 | Notion Integration | `src/integrations/notion/client.py` |
| 4 | Google Drive Integration | `src/integrations/gdrive/client.py` |
| 5 | Gmail Integration | `src/integrations/gmail/client.py` |
| 6 | Notification Scheduler | `src/core/scheduler.py` |
| 7 | AI Agent Orchestration | `src/agents/dispatcher.py` |
| 8 | Multi-step Workflows | `src/core/workflows.py` |
| 9 | Personal Knowledge Libraries | `src/core/libraries.py` |

---

## Knowledge Terms

**Library**
The filesystem-based personal knowledge store under `library/`. Contains markdown files organized by section: `profile/`, `terms/`, `books/`, `articles/`, `thoughts/`, `references/`, `research/`.

**Research Bundle**
A directory created during deep capture containing 7 structured markdown files: `index.md`, `01-raw-input.md`, `02-search-history.md`, `03-research-notes.md`, `04-information-to-track.md`, `05-qa-log.md`, `06-logic-trail.md`, `07-conclusion.md`.

**Deep Capture**
The "add to library" flow that uses Gemini AI to analyze, categorize, and structure a knowledge intake into a research bundle plus supporting entries.

**Bundle Index**
The `index.md` file inside a research bundle. Contains the summary, key facts, and information to track.

**Library Index**
The generated `library/index.json` file that catalogs all entries and bundles for fast search.

**Search Cache**
An in-memory LRU cache with 5-minute TTL for library search results. Invalidated on every write.

**9-Field Standard**
The mandatory metadata order for library entries: Title, Type/Category, Status, Priority/Confidence, Summary/Definition, Key Points, Relations, Source, Date Added/Updated.

---

## Integration Terms

**Workflow**
A multi-step command that chains integrations. Examples: inbox-to-notion, inbox-to-drive, notion-to-drive.

**Scheduler**
The APScheduler-based background job system for reminders, daily digests, and weekly maintenance. Started in the FastAPI lifespan hook.

**Digest**
A proactive summary pushed on a schedule. Currently: daily Gmail digest (optional, disabled by default).

**Reminder Store**
The JSON file (`data/reminders.json`) that persists scheduled reminders across restarts.

**Service Account**
The authentication method used for Google Drive (server-to-server). Contrast with Gmail, which requires OAuth2.

**OAuth2 Flow**
The browser-based consent flow used for Gmail authentication. Tokens are cached to `.gmail_token.json`.

---

## AI Governance Terms

**RL Level**
Responsibility Level (RL1 through RL5). Defines what an AI agent is authorized to do without human approval. Higher levels = more autonomy.

**Task Card**
A structured task definition using the template in `docs/templates/task-card-template.md`. Contains objective, acceptance criteria, execution plan, test protocol, and handoff summary.

**OKR**
Objectives and Key Results. Used in `docs/ai-employer-operating-system.md` to score AI performance against repository goals.

**Decision Record**
A formal record in `docs/decisions/NNN-slug.md` documenting a significant architectural or policy choice.

**Approval Gate**
The rule that policy/governance/process updates require explicit owner approval before execution.

---

## Command Terms

**Command**
A text string sent to the POST `/command` endpoint. Examples: `"status"`, `"add to library: second order thinking"`, `"email"`.

**Trigger Keyword**
A substring in `INTENT_MAP` that causes an intent match. Example: `"add to library"` triggers `library_capture`.

**Compound Workflow Detection**
Special logic that runs before keyword matching to detect multi-step commands by combining tokens (e.g., `inbox` + `summarize` + `save` → `workflow`).
