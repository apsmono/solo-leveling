# Phase 2 — User Setup (Live n8n Provisioning)

This is the only part of Phase 2 that cannot be automated: it needs a running
n8n instance with an API key and two activated workflows. Everything else is
code-complete and tested offline.

## Status

- n8n is already running locally: `http://localhost:5678` (docker-compose.n8n.yml, `projects-n8n-1`). `GET /healthz` returns 200.

## Steps

### 1. Generate an n8n API key

1. Open `http://localhost:5678` and sign in (basic auth from `docker-compose.n8n.yml`:
   user `admin`, password `changeme-strong-password` — change these for any non-local use).
2. Go to **Settings → API → Create API Key**. Copy the key.

### 2. Configure the brain

In `solo-leveling/.env`:

```dotenv
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=<the key you just created>
```

Verify connectivity:

```bash
cd solo-leveling && source .venv/bin/activate
python -c "from src.n8n.client import health_check; print(health_check())"
# expect: {'ok': True}
```

### 3. Build + activate the two starter workflows

Create these in the n8n UI and **activate** them:

- **Read-only** (`gmail_read_summary`): Gmail "get many messages" → summarize/format. No side effects.
- **Side-effecting** (`gmail_send_draft`): compose → Gmail "send". This is the one that must pass the RL approval gate.

### 4. Record the real workflow IDs

Each workflow has a numeric ID (visible in its URL / settings). Replace the
`n8n_workflow_id: 0` placeholders:

- `solo-leveling/src/n8n/templates/gmail_read_summary.json`
- `solo-leveling/src/n8n/templates/gmail_send_draft.json`

### 5. Verify end-to-end

```bash
# read-only trigger through the brain
python -c "import asyncio; from src.n8n.executor import execute_intent; print(asyncio.run(execute_intent('summarize my gmail', {'max_messages': 5})))"
# then confirm the run appears in the n8n UI and in data/n8n_executions.json
```

- Sync a Gmail credential and confirm it appears (and is usable in a node) in the n8n UI — the owner never pastes a raw key.
- Trigger the side-effecting workflow and confirm it returns `needs_approval` at the default RL (RL1).

## Acceptance (from 02-VALIDATION.md "Manual-Only Verifications")

- [ ] `health_check()` returns `{'ok': True}` against the live instance
- [ ] Both template JSONs have non-zero `n8n_workflow_id` matching activated workflows
- [ ] A live read-only trigger produces an execution in the n8n UI + an entry in `data/n8n_executions.json`
- [ ] A synced Gmail credential is visible/usable in the n8n UI
