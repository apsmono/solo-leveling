# solo-leveling

Central brain and command center for personal development, financial freedom, and connected-tool automation.

## What This Repository Does

This repository is the persistent memory, decision log, and orchestration layer for the owner's entire personal operating system. It connects to Notion, Google Drive, Gmail, and WhatsApp. The owner sends commands via WhatsApp; the brain routes them, coordinates AI agents, and writes results back to connected tools.

## AI-Ready Workspace

This repository is built AI-first. GitHub Copilot and other AI agents work from a shared set of authoritative context files so every AI task operates against current reality.

Source-of-truth files:

- `AGENTS.md` — repository-wide agent rules and changelog standard.
- `AI_CONTEXT.md` — project intent, current phase, and active planning documents.
- `.github/copilot-instructions.md` — GitHub Copilot-specific working rules.
- `CHANGELOG.md` — human-readable running history of notable changes.
- `docs/architecture/command-center.md` — full brain and command-center architecture.
- `docs/architecture/integrations.md` — integration map for all connected services.
- `docs/decisions/` — formal decision records for major scope, structure, or policy changes.
- `AI_INSTALLATION.md` — reusable setup guide and bootstrap prompt for other projects.

## Documentation Structure

```text
docs/
  architecture/       → system design and integration specs
  decisions/          → formal decision log
  self-development-system.md
  financial-freedom-strategy.md
  habit-system.md
  review-rhythm.md
  decision-log-template.md
src/                  → integration code and connectors (future)
prompts/              → reusable AI prompts
```

Start from `docs/README.md` for the full document map.

## Container Run

Build the image:

```bash
docker build -t solo-leveling .
```

Run the webhook server with persistent mounts for runtime writes:

```bash
docker run --rm \
  -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/library:/app/library" \
  -v "$(pwd)/data:/app/data" \
  solo-leveling
```

The mounts matter because Stage 9 writes to `library/` and the reminder scheduler writes to `data/`.
