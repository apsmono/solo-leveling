# Railway Setup Runbook

Date: 2026-04-23 11-02-18
Prepared by: GitHub Copilot
Status: Active — use this as your step-by-step execution guide

---

## What You Are Building

A publicly reachable HTTPS FastAPI webhook that:
- Receives WhatsApp messages from Meta
- Routes commands to Notion, Drive, AI agents, and library handlers
- Persists reminder data and library files across deploys

---

## Pre-Conditions (Done Before Starting)

- [x] Registered Railway account
- [x] Repository pushed to GitHub
- [x] Dockerfile exists in repository root
- [x] `.env` fully prepared locally
- [x] All integration credentials validated locally

---

## Part 1: Railway Project Setup

### Step 1 — Connect GitHub repo

1. Log in at railway.com
2. Click **New Project**
3. Choose **Deploy from GitHub repo**
4. Authorize Railway to access your GitHub account if not already done
5. Select the `solo-leveling` repository
6. Railway will detect the Dockerfile automatically

### Step 2 — Confirm build settings

1. Inside the new project, open your service settings
2. Ensure **Source** is set to your GitHub repo and branch is `main`
3. Ensure **Builder** is set to **Dockerfile** (not Nixpacks)
4. Set **Watch Paths** to `/` (root) so all code changes trigger redeploys
5. Confirm the **Start Command** is empty or auto-detected from your Dockerfile's CMD

### Step 3 — Set environment variables

Go to **Variables** tab for the service. Add each variable individually (do NOT upload `.env` as a file):

```
WHATSAPP_PROVIDER=meta
WHATSAPP_OWNER_NUMBER=+628113301665
META_PHONE_NUMBER_ID=<your value>
META_ACCESS_TOKEN=<your value>
META_VERIFY_TOKEN=<your value>
NOTION_API_TOKEN=<your value>
NOTION_WORKFLOW_PARENT_ID=<your value>
GOOGLE_DRIVE_CREDENTIALS_PATH=/app/.credentials/google/service_account.json
GMAIL_ENABLED=false
AGENT_PROVIDER=openai
OPENAI_API_KEY=<your value when ready>
ANTHROPIC_API_KEY=<your value when ready>
```

Note on GMAIL_ENABLED: keep `false` until you are ready to wire Gmail in production. Re-enable by changing to `true`.

Note on Google credentials files: these are JSON files, not plain values. See Part 2 for how to handle them.

### Step 4 — Handle credential files (JSON secrets)

Google Drive and Gmail use JSON credential files, not plain strings. Railway does not natively mount secret files. Options:

**Option A (recommended for now): inline JSON as env vars (supported now)**
1. Open your `service_account.json` file
2. Copy the entire JSON content in one line (minified)
3. Add as Railway variable: `GOOGLE_DRIVE_CREDENTIALS_JSON=<minified json>`
4. For Gmail (when re-enabled), add: `GMAIL_CREDENTIALS_JSON=<minified oauth client json>`
5. This project now reads these env vars directly and falls back to file paths when needed
6. This avoids any file-mounting complexity for credential files

**Option B: Volume-mounted file (when Railway supports it in your plan)**
1. Create a Railway volume
2. Mount it at `/app/.credentials`
3. Upload credential files into the volume
4. Set `GOOGLE_DRIVE_CREDENTIALS_PATH=/app/.credentials/google/service_account.json`

Option A is production-ready in this repository.

### Step 5 — First deploy

1. Trigger a deploy from the **Deployments** tab or by pushing a commit to `main`
2. Watch the build logs — the Dockerfile will be built and the container launched
3. Wait for `Application startup complete` in logs
4. Railway assigns a public domain like `<your-project>.up.railway.app`

---

## Part 2: Verify Deployment

### Health check

```bash
curl https://<your-project>.up.railway.app/docs
# Expected: 200 OK, FastAPI docs page loads
```

### Webhook verification (Meta)

Your Meta webhook callback URL is:
```
https://<your-project>.up.railway.app/webhook/whatsapp
```

The webhook verify token must match `META_VERIFY_TOKEN` in Railway variables.

---

## Part 3: Meta Webhook Registration

1. Open Meta for Developers → your WhatsApp app
2. Go to WhatsApp → Configuration
3. Set **Callback URL** to `https://<your-project>.up.railway.app/webhook/whatsapp`
4. Set **Verify Token** to the same value as your `META_VERIFY_TOKEN` env var
5. Click **Verify and Save**
6. Subscribe to **messages** webhook field

---

## Part 4: Persistence (Library and Reminders)

Railway volumes allow persistent file storage across deploys. This is needed for:
- `library/` — Stage 9 knowledge entries
- `data/reminders.json` — scheduled reminders

### Steps

1. In Railway dashboard, open your service
2. Go to **Volumes** section
3. Create a volume, mount path `/app/data` (for reminder persistence)
4. Create a second volume, mount path `/app/library` (for library persistence)

Important: without volumes, `library/` and `data/` are reset on every redeploy. This is acceptable during early testing but must be set up before going into regular use.

---

## Part 5: Deployment Checklist (Run These In Order)

- [ ] GitHub repo connected and Dockerfile detected
- [ ] All env vars added to Railway Variables
- [ ] First deploy succeeded (no container crash in logs)
- [ ] `curl /docs` returns 200
- [ ] Meta webhook verification passes
- [ ] volumes created and mounted for `library/` and `data/`
- [ ] Send test WhatsApp message: "health" → should return ✅/❌ status report
- [ ] Send test WhatsApp message: "status" → should return "Brain is online"
- [ ] Confirm reminder persistence: add reminder, redeploy, check it survives

---

## Part 6: Ongoing Operations

### Redeploy on code changes

Every push to `main` triggers an automatic redeploy. Monitor in the Railway dashboard.

### View logs

```bash
# In Railway dashboard: Deployments → click deploy → Logs
# Or install Railway CLI:
railway login
railway logs
```

### Rollback

If a deploy breaks, Railway keeps the previous successful image. Click **Rollback** in Deployments to revert immediately.

### Set spending limits

In Railway dashboard → Billing:
- Set a monthly spending cap to avoid unexpected charges
- Enable usage alerts/emails at a threshold that is comfortable

---

## Part 7: Considerations And Gotchas

| Topic | Detail |
|---|---|
| Cold start | Railway keeps your container running. No cold start by default on paid plans. |
| Domain stability | Railway gives `*.up.railway.app` by default. Register a custom domain to avoid URL churn when switching plans. |
| Secrets in logs | Never log env var values. Double-check your app does not print credentials on startup. |
| File persistence | If volumes are not mounted, library and data resets on redeploy. Mount before storing real data. |
| GMAIL_ENABLED | Currently `false`. Gmail OAuth flow requires interactive browser step — cannot run headless in production without token caching. Re-enable when ready. |
| Watch PATH CI | Railway auto-deploys on push to `main`. Make sure CI tests pass before merging to main. |
| Meta webhook URL change | If you change Railway domains, you must re-register the webhook in Meta dashboard. Use a stable custom domain to avoid this. |
| Free tier limits | Railway free tier has usage credits. Watch spend especially during active testing. |

---

## Next Action When Railway Is Live

1. Register Meta webhook callback URL with the Railway public URL.
2. Test "health" command via WhatsApp.
3. Create volumes for `library/` and `data/`.
4. Set up custom domain when traffic stabilizes.
5. Set spending cap.
