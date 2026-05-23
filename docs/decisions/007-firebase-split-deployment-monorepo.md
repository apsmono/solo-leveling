# 007 — Firebase Ecosystem, Split Deployment, Telegram, and Monorepo Structure

## Status

Accepted

## Date

2026-05-03

## Scope

Backend architecture, database strategy, authentication, deployment topology, messaging interface, and repository organization.

## Context

The project had no persistent database (only JSON files), no authentication, no frontend, no messaging interface beyond a raw HTTP endpoint, and no clear structure for future sub-projects. The owner wanted to:

1. Use Firebase for database and auth
2. Host a dashboard on GitHub Pages with the backend on a MacMini
3. Replace WhatsApp with Telegram
4. Support sub-projects in the same repo

## Decision

1. **Firebase Admin SDK** for server-side auth (ID token verification) and Firestore for structured data.
2. **Single-user login gate** via Firebase Auth: only `/dashboard` and `/api/v1/*` require auth; public endpoints (`/healthz`, `/command`) remain open.
3. **Firestore replaces JSON files** for reminders and command history, gated by `USE_FIRESTORE_REMINDERS` feature flag with JSON fallback for local dev.
4. **Split deployment**: FastAPI backend runs on MacMini via Docker Compose; static dashboard frontend deploys to GitHub Pages.
5. **Telegram webhook** supplements (not replaces) the existing HTTP `/command` endpoint.
6. ~~Monorepo structure with `subprojects/` directory~~ **RESCINDED** — subprojects were extracted into standalone repos managed by a parent workspace repo (`apsmono/projects`) using git submodules. See amendment below.

## Why

- Firebase provides managed auth and NoSQL without self-hosting a database.
- Single-user keeps auth simple (no RBAC complexity) while still protecting dashboard data.
- Feature flag preserves local development without requiring Firebase credentials.
- GitHub Pages is free and ideal for static sites; MacMini provides full Python runtime control.
- Telegram bot API is simpler than WhatsApp Business API (no Meta verification).
- Monorepo keeps related projects discoverable and shareable.

## Consequences

### Positive

- Backend and frontend are independently deployable.
- Firestore enables real-time data queries for the dashboard.
- Telegram provides a second command interface with minimal setup.
- Sub-project scaffolding is ready for future expansion.

### Trade-offs

- CORS is required for GitHub Pages → MacMini API calls.
- MacMini must have reliable internet and HTTPS (Cloudflare Tunnel or reverse proxy).
- Firestore introduces a new external dependency; JSON fallback mitigates this for local dev.
- Frontend uses vanilla JS (no framework) to avoid build complexity; may need migration if the UI grows beyond ~5 screens.

## Implementation Notes

- `src/integrations/firebase/` — auth and firestore modules
- `src/integrations/telegram/` — webhook handler
- `src/api/` — versioned REST API with auth dependencies
- `frontend/` — static site for GitHub Pages
- `docker-compose.yml` — MacMini orchestration
- `subprojects/` — convention-driven sub-project directory
