# solo-leveling

Central brain and command center for personal development, financial freedom, and connected-tool automation.

## What This Repository Does

This repository is the persistent memory, decision log, and orchestration layer for the owner's entire personal operating system. It connects to Notion, Google Drive, and Gmail, and exposes an API/CLI-first command interface. The brain routes commands, coordinates AI agents, and writes results back to connected tools.

## AI-Ready Workspace

This repository is built AI-first. GitHub Copilot and other AI agents work from a shared set of authoritative context files so every AI task operates against current reality.

**New to this repo?** Start with [`CLAUDE.md`](CLAUDE.md) — the AI onboarding hub that connects all documentation.

Source-of-truth files:

- `AGENTS.md` — repository-wide agent rules and changelog standard.
- `AI_CONTEXT.md` — project intent, current phase, and active planning documents.
- `CLAUDE.md` — AI onboarding hub connecting all docs, conventions, and architecture.
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

## Runbook

### Local development (no Docker)

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run all tests (23 tests, 3 credential-gated skips are expected)
python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v

# 3. Start the API server
uvicorn src.app:app --port 8000 --reload
```

### Container run (with mounts)

```bash
docker build -t solo-leveling .

docker run --rm \
  -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/library:/app/library" \
  -v "$(pwd)/data:/app/data" \
  solo-leveling
```

**Expected startup output:**
```
INFO:     Started server process [1]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Optional credential warnings at startup are expected and not fatal:
```
WARNING: Optional credentials not set (integrations will be skipped): ...
```

### Health check

```bash
# /docs returns 200 when the app is running
curl http://localhost:8000/docs
```

Or use the built-in `health` command through the command API:

```bash
curl -s -X POST http://localhost:8000/command \
  -H 'Content-Type: application/json' \
  -d '{"text":"health"}'
```

### Container restart behaviour

- Reminders persist across restarts via the mounted `data/` volume (`data/reminders.json`).
- If `data/` is not mounted, unsent reminders are lost on restart.
- Scheduler jobs (due-reminders, daily-digest, library-maintenance) are re-registered on every startup.
- Library entries in `library/` persist across restarts via the mounted `library/` volume.

### Credential setup

See `docs/SETUP_SECRETS.md` for the full credential checklist.
Quick order: Notion → Google Drive + Gmail → AI provider (Gemini primary).

### Run a single test group

```bash
# Stage 9 library tests only
python -m unittest tests.test_stage9_libraries -v

# Integration smoke tests only
python -m unittest tests.test_integration_smoke -v
```
