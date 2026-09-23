# AI & AI-Agents Environment

This workspace has two distinct senses of "AI agent". Keep them separate:

1. **In-product agents** — the LLM-powered subsystems that *run inside* the `solo-leveling` brain (Gemini dispatcher, Autopilot, RL governance). These are application features.
2. **Coding agents** — assistants like **Claude Code** that *edit this workspace*. Rules for those are below and in `AGENTS.md` / `CLAUDE.md`.

---

## Part 1 — In-product AI agents (inside the brain)

All of this lives in `solo-leveling/`. Deep detail: `solo-leveling/docs/architecture/` and `solo-leveling/docs/decisions/`.

### LLM providers

| Provider | Where | Used for |
|---|---|---|
| **Gemini** (`gemini-2.0-flash`) | `src/agents/dispatcher.py` via REST (`httpx`) | primary "AI employee" — deep capture, ask-AI, workflow summaries, autopilot planning |
| **Kimi** (via `litellm`) | `src/agents/kimi_client.py` | autopilot reasoning |

`run_agent(task, context="", system="")` is the single Gemini entry point. The provider is selected by `AGENT_PROVIDER` (default `gemini`); the key is `GEMINI_API_KEY`; the model is overridable via `GEMINI_MODEL`.

### The Dispatcher pattern

A command is classified to an intent (`core/router.py`), and AI-backed handlers call `run_agent()` with a task-specific system prompt. The LLM returns structured (often JSON) output the handler then acts on. There is no long-lived conversational memory — context is assembled per call from the library, the command, and integration data.

### Autopilot — autonomous task execution

`src/autopilot/` implements a plan→execute→observe loop:

- **planner.py** — Gemini turns a goal into an ordered JSON step plan.
- **loop.py** — a ticker loads the active task, executes the current step via the tool registry, records the observation, and advances.
- **tools.py** — the registry of callable actions (read, bash, gmail_read, library_index, …). This is the autopilot's "hands".
- **governor.py** — the safety gate. Every step is validated against the configured **Responsibility Level** before it runs.

Commands: `autopilot start: <goal>`, `autopilot status`, `autopilot pause`, `autopilot approve`.

State persists as JSON under `data/` (`autopilot_tasks.json`, `autopilot_state.json`, `autopilot_approvals.json`).

### Responsibility Levels (RL1–RL5)

The governance model (see `docs/decisions/003-ai-employer-governance-model.md`) bounds autonomy:

| RL | Role | Allowed | Human gate |
|----|------|---------|-----------|
| RL1 | Assisted | read-only | review every step |
| RL2 | Independent Task | read + local file writes | log only |
| RL3 | Cross-Module Integrator | + git commit | notify after |
| RL4 | Lead Executor | cross-service writes | pre-approval queue |
| RL5 | Program Lead | destructive ops | always explicit approve |

Configured by `AUTOPILOT_RL_LEVEL` (default `1`). `AUTOPILOT_MAX_STEPS_PER_TASK` caps runaway loops.

### Safety mechanisms

- **Sensitive-content filter** in library capture blocks passwords, API keys, identity numbers, and contact details from being stored.
- **RL governor** gates autopilot actions.
- **Firebase Auth** gates dashboard `/api/v1/*` endpoints; `ALLOWED_USER_EMAIL` enforces single-user access.
- **Telegram webhook** validates the bot token / webhook secret.
- Integrations are wrapped in try/except; failures are logged, not fatal.

### Knowledge / memory (Stage 9 libraries)

The brain's "memory" is the **local-first markdown library** (`library/`), not a vector DB. Deep Capture produces a 7-file research bundle per topic via Gemini; `index.json` backs search. This is the substrate the AI handlers read context from.

### Environment variables (AI-relevant subset)

From `solo-leveling/.env.example` — full list there:

```
AGENT_PROVIDER=gemini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash

AUTOPILOT_RL_LEVEL=1
AUTOPILOT_MAX_STEPS_PER_TASK=10
AUTOPILOT_TASK_STORE_PATH=data/autopilot_tasks.json
AUTOPILOT_STATE_PATH=data/autopilot_state.json
AUTOPILOT_APPROVALS_PATH=data/autopilot_approvals.json
```

Integrations (Notion, Google Drive, Gmail, Firebase, GitHub, Telegram) each have their own credential vars — see `.env.example`.

---

## Part 2 — Coding agents working in this workspace

These rules are for assistants (Claude Code and similar) editing the repo.

### Submodule awareness (most important)

This is a **submodule workspace**. Before editing, know which repo you're in:

- Code for a project lives in its submodule directory; commit **inside** the submodule, then record the new SHA in the parent (`git add <submodule>` + commit). See `CONVENTIONS.md`.
- A change "in the parent" usually means a docs edit, a scaffolding edit, or a submodule SHA bump — not project source.
- Never commit a parent pointer to a submodule commit you haven't pushed.

### Respect each project's own docs

`solo-leveling/` carries its own `CLAUDE.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `GLOSSARY.md`, `REPO_MAP.md`, and `AI_CONTEXT.md`. When working inside it, those are authoritative and more detailed than the workspace-level files. `AI_CONTEXT.md` is the **source of truth for the current phase and priorities** of the brain.

### Don't leak secrets

`.env`, `.credentials/`, service-account JSON, and tokens are gitignored and must never be committed or printed. Frontend Firebase web config is public; backend credentials are not.

### Verify before claiming done

- Brain: run `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v` (offline). Live integrations require explicit env flags.
- Frontends: build/serve and check in a browser; don't assert a UI works from code inspection alone.

### Stay in scope

Bug fixes don't need surrounding refactors. Match the change to the request. Push project-specific depth into the submodule's docs, not the workspace-level files.
