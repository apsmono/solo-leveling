# Dashboard (static site)

Portfolio landing (`index.html` + `portfolio.css`) and an authenticated **command center** under `dashboard/` (library stats, integration health, command history, reminders, raw command sender).

## Configure before deploy

1. **`shared/firebase-config.js`** — Replace placeholders with your Firebase web app config (Console → Project settings). Set **`API_BASE`** to your FastAPI origin (MacMini / Railway), for example `https://your-host.example.com`.
2. **Backend** — Set `FRONTEND_ORIGIN` to your GitHub Pages site origin (scheme + host, no trailing slash) so the browser can call `/api/v1/*` with CORS. Firebase Admin must accept the same Google sign-in project as the web config.

## Deploy

- **Monorepo → GitHub Pages:** `.github/workflows/deploy-dashboard.yml` uploads `./subprojects/dashboard` on every push to `main`.
- **Standalone `apsmono/dashboard`:** `.github/workflows/sync-subprojects.yml` mirrors this folder on each `main` push (requires `SYNC_PAT`).

## Local preview

Serve the folder with any static server from `subprojects/dashboard` (Firebase Auth popup requires `http://localhost` or HTTPS; use `python -m http.server` from this directory for quick checks).
