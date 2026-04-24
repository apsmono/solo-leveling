# src — Integration Code

This folder holds all executable code for the command center brain.

## Structure

```
src/
  integrations/
    notion/        → Notion read/write connector
    gdrive/        → Google Drive read/write connector
    gmail/         → Gmail read connector
    notifications/ → Outbound notification dispatcher
  core/
    router.py      → Command intent parser and dispatcher
    config.py      → Environment variable loader (no secrets stored here)
    scheduler.py   → Reminder persistence and proactive notification jobs
    workflows.py   → Stage 8 multi-step command composition layer
  agents/
    dispatcher.py  → AI agent spawner and result collector
  app.py           → FastAPI command server (`/command`, `/healthz`)
```

## Setup Rules

- All secrets and API keys go in `.env` (never committed).
- Copy `.env.example` and fill in values before running any integration.
- Each integration folder has its own `README.md` with setup and verification steps.

## Running

Each integration can be tested independently. See the `README.md` in each subfolder.
