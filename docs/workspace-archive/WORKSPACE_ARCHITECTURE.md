# Architecture

Big-picture architecture of the `apsmono/projects` workspace. For deep brain internals, read `solo-leveling/ARCHITECTURE.md` and `solo-leveling/docs/architecture/`.

## Workspace shape

The workspace is a **constellation of independent projects** pinned together by a parent repo. There is no shared runtime or shared build — the only coupling is:

1. The **parent repo** records which commit of each submodule is "current".
2. The **dashboard** frontend talks to the **solo-leveling** backend over HTTP.

```
                         apsmono/projects (parent)
                                  │ pins SHAs
        ┌───────────┬─────────────┼─────────────┬──────────────────┐
        ▼           ▼             ▼             ▼                  ▼
  solo-leveling  apsmono.      dashboard   wedding-invitation    koperasi
  (FastAPI brain) github.io    (static UI)    (React SPA)      (static page)
                 (portfolio)       ▲
                                   │
                    REST /api/v1 + /command (Firebase-auth'd)
                                   │
                        dashboard command center calls the brain
```

Deployment is per-project and independent:

| Project | Target | Mechanism |
|---|---|---|
| solo-leveling | MacMini (Docker) / Railway | `docker compose up -d`, health at `/healthz` |
| apsmono.github.io | GitHub Pages | `npm run build` → `dist/` via `.github/workflows/deploy.yml` |
| dashboard | GitHub Pages | `.github/workflows/deploy.yml` |
| wedding-invitation | GitHub Pages / Cloudflare / Vercel | `bun run build` → `dist/` |
| koperasi | Cloudflare Pages | static upload |

## The brain (solo-leveling) — layered architecture

The brain is the only architecturally significant service. It is a single FastAPI process with four conceptual layers:

```
┌─────────────────────────────────────────────────────────────┐
│ Command Interface   POST /command · /webhook/telegram         │
│                     /api/v1/* (dashboard, Firebase-auth'd)    │
├─────────────────────────────────────────────────────────────┤
│ Brain Core          router.py  → intent detection & dispatch  │
│                     workflows.py (Stage 8 chains)             │
│                     libraries.py (Stage 9 knowledge store)    │
│                     scheduler.py (APScheduler background jobs) │
├─────────────────────────────────────────────────────────────┤
│ AI Agent Layer      agents/dispatcher.py  → Gemini (primary)  │
│                     autopilot/  → planner · governor · tools  │
│                     agents/kimi_client.py → Kimi (autopilot)  │
├─────────────────────────────────────────────────────────────┤
│ Integration Layer   notion · gdrive · gmail · firebase ·      │
│                     github · telegram  (one client per svc)   │
└─────────────────────────────────────────────────────────────┘
        │ local-first state
        ▼
  library/ (markdown + index.json)   data/ (reminders, autopilot tasks)
  Firebase Firestore (optional dual backend)
```

### Three execution patterns

The brain handles work in three distinct ways — understanding these explains most of the codebase:

1. **Synchronous dispatch** — A command arrives → `route_command()` detects the intent via `INTENT_MAP` → the matching handler runs (possibly calling Gemini or an integration) → a reply is returned. This is the default path for `/command` and Telegram.

2. **Asynchronous automation** — `scheduler.py` (APScheduler) runs background jobs on a poll loop: due reminders, optional daily Gmail digest, optional weekly library maintenance. Started/stopped by the FastAPI lifespan in `app.py`.

3. **Autonomous loop (Autopilot)** — A goal is planned into steps by Gemini (`planner.py`), persisted as a task, then a ticker advances the task one step at a time (`loop.py`): execute a tool from the registry → record the observation → advance. Every step is checked by the **Governor** against the configured **Responsibility Level (RL1–RL5)**, which gates how much autonomy is allowed before requiring human approval.

### Intent routing

`core/router.py` is the spine. `INTENT_MAP` maps ~25 intents to keyword triggers; `_detect_intent()` does longest-match keyword detection plus special prefix handling (`autopilot …`, GitHub commands); `_dispatch()` invokes the handler and optionally logs the command to Firestore.

### State & persistence (local-first)

- `library/` — knowledge stored as markdown files in section folders; `library/index.json` is regenerated on every write and backs full-text search (with an in-memory LRU + TTL cache).
- `data/` — `reminders.json` and `autopilot_*.json` hold runtime state.
- **Firebase Firestore** is an *optional* dual backend for reminders and the command log; the brain runs fully without it.

### AI providers

- **Gemini** (`gemini-2.0-flash` by default) is the primary LLM via direct REST (`httpx`) in `dispatcher.py` — used for library deep capture, "ask AI", workflow summaries, and autopilot planning.
- **Kimi** (via `litellm`) backs autopilot reasoning. The Gemini-primary decision is recorded in `docs/decisions/006-interface-and-gemini-pivot.md`.

## Extending the brain

- **New command** — add an intent + triggers to `INTENT_MAP`, write a handler, wire it in `_dispatch()`.
- **New integration** — add a client module under `src/integrations/<service>/`, expose typed functions, call it from a handler or workflow.
- **New workflow** — compose existing integration calls in `core/workflows.py` behind an intent detector.

## Frontend architectures (brief)

- **apsmono.github.io** — portfolio site; Vite + React 19 + Tailwind CSS 4. Custom domain `apsmono.com`. Embeds dashboard at `/dashboard/` path.
- **dashboard** — static site; Firebase Auth (Google popup) gates a command-center UI with four views (overview, commands, reminders, cmd). `api.js` wraps fetch with a Firebase ID token bearer; `API_BASE` in `shared/firebase-config.js` points at the deployed brain.
- **wedding-invitation** — React 19 SPA: ~12 section components (hero, story, countdown, events, gallery, RSVP→WhatsApp, etc.), Zustand store, custom hooks (`useCountdown`, `useScrollSpy`), Framer Motion animations.
- **koperasi** — single static landing page (`index.html` + `css/base.css` + `js/main.js`): responsive nav, scroll effects, contact-form stub.
