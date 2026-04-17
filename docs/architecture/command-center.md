# Command Center Architecture

## Purpose

This repository is the central brain that orchestrates personal development, financial planning, and automation across all connected tools and services. It receives commands, decides what to do, coordinates AI agents, and writes results back to connected systems.

## Role Of This Repository

| Role            | Description                                                                 |
| --------------- | --------------------------------------------------------------------------- |
| Brain           | Holds persistent context, goals, strategies, and operating rules            |
| Command router  | Receives commands from WhatsApp (and future interfaces) and dispatches work |
| Integration hub | Connects to Notion, Google Drive, email, and other services                 |
| AI orchestrator | Spawns and directs AI agents for complex tasks                              |
| Memory          | All docs, decisions, and strategies are the persistent state of the brain   |

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│              COMMAND INTERFACES                  │
│   WhatsApp · CLI · (future: web, voice)          │
└─────────────────────┬───────────────────────────┘
                      │ command received
┌─────────────────────▼───────────────────────────┐
│                  BRAIN CORE                      │
│   This repository                               │
│   Parses intent · Routes · Tracks state         │
└────────┬───────────────────────┬────────────────┘
         │                       │
┌────────▼────────┐   ┌─────────▼────────────────┐
│  AI AGENT LAYER │   │   INTEGRATION LAYER       │
│  GitHub Copilot │   │   Notion                  │
│  Claude API     │   │   Google Drive            │
│  OpenAI API     │   │   Gmail                   │
│  Custom agents  │   │   WhatsApp (outbound)     │
└─────────────────┘   │   Notifications           │
                      └───────────────────────────┘
```

## Data Flow

1. **Command received** — user sends a message via WhatsApp (or CLI).
2. **Brain parses intent** — the command is matched to an action or workflow.
3. **Dispatch** — the brain either:
   - Calls an integration directly (e.g. read a Notion page, create a GDrive file), or
   - Spawns an AI agent to reason about the request and produce a result, or
   - Both: AI produces content, integration writes it to the target tool.
4. **Result returned** — output is written back to the user via the command interface.
5. **State updated** — decisions, outputs, and meaningful changes are written back to `docs/` and `CHANGELOG.md`.

## Command Interface: WhatsApp

- User sends natural-language commands to a WhatsApp number controlled by the brain.
- The bot parses intent and routes to the correct handler.
- Responses and confirmations are sent back to the same WhatsApp chat.
- Security: only messages from a trusted number (the owner) are processed.

See `docs/architecture/integrations.md` for implementation options.

## AI Agent Layer

The brain can delegate tasks to AI agents for:

- Drafting documents or strategies
- Summarizing emails or Notion pages
- Generating plans or analyses
- Reviewing and improving existing content

AI agents are directed by prompts stored in `prompts/` and context from `docs/`.

## Persistent Memory

The brain's memory is this repository:

- `docs/` holds strategy, plans, and decisions
- `docs/decisions/` holds formal decision records
- `CHANGELOG.md` records what changed and when
- `AI_CONTEXT.md` tells any AI agent the current state of the project

When the brain processes a command and produces a durable output, it writes the result back to the correct doc file.

## Security Principles

- No credentials or secrets are stored in this repository.
- All API keys, tokens, and secrets go into environment variables or a secrets manager.
- The WhatsApp command interface only processes messages from the owner's number.
- Any integration that can write to external systems requires explicit confirmation before destructive actions.

## Implementation Stages

| Stage                        | Scope                                                     | Status      |
| ---------------------------- | --------------------------------------------------------- | ----------- |
| 1 — Foundation               | Architecture docs, decision records, repository structure | Done        |
| 2 — WhatsApp bot             | Receive and route commands from the owner                 | Done        |
| 3 — Notion integration       | Read and write Notion pages and databases                 | Done        |
| 4 — Google Drive integration | Read and write GDrive files                               | Done        |
| 5 — Gmail integration        | Read, summarize, and triage emails                        | Done        |
| 6 — Notifications            | Push reminders, digests, and status updates back to user  | Done        |
| 7 — AI agent orchestration   | Spawn AI agents for complex tasks via API                 | Done        |
| 8 — Full command routing     | Multi-step workflows combining all layers                 | In progress |

## Stage 6 Implementation Notes

- Scheduler implementation lives in `src/core/scheduler.py`.
- Runs as an APScheduler background worker inside the FastAPI webhook process.
- Persists reminder jobs to `data/reminders.json` so reminders survive restarts.
- Current user-facing command formats:
  - `remind me in 30 minutes to stretch`
  - `remind me tomorrow at 09:00 to review goals`
  - `remind me at 2026-04-18 08:30 to plan the day`
  - `reminders`
- Optional daily Gmail digest can be enabled with `DAILY_GMAIL_DIGEST_ENABLED=true`.

## Stage 8 Implementation Notes (Starter)

- Initial workflow composition layer lives in `src/core/workflows.py`.
- Implemented first chain: `summarise my inbox and save to notion`.
- Current flow:
  1. Read Gmail unread summary.
  2. Create a Notion page with that summary.
- Required setup for this workflow:
  - `NOTION_API_TOKEN`
  - `NOTION_WORKFLOW_PARENT_ID`
  - Gmail credentials and token setup.
- Until secrets are configured, workflow handlers return actionable setup guidance instead of crashing.
