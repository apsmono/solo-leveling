# Railway Deployment & Health Check Workflow

**Date:** 2026-04-23
**Purpose:** Step-by-step guide from code -> deployed on Railway -> health verified

---

## Pre-Deployment Checklist (Verify Locally First)

Before you touch Railway, complete these on your local machine:

### 1. Verify Local Health

```bash
cd /Users/macmini/Documents/projects/solo-leveling
python3 -c "from src.core.router import route_command; print(route_command('health'))"
```

**Expected output includes:**
```
✅ Notion (NOTION_API_TOKEN set)
✅ Google Drive ( set)
```

If you see missing critical credentials, gather them before continuing.

### 2. Run Full Test Suite

```bash
.venv/bin/python -m unittest discover -v
```

**Expected:** `Ran 37 tests in 0.236s OK (skipped=3)`

### 3. Start Server Locally (5-minute validation)

```bash
.venv/bin/python -m uvicorn src.integrations.whatsapp.handler:app --port 8000
```

In another terminal:
```bash
curl http://localhost:8000/docs
```

**Expected:** HTTP 200, FastAPI Swagger UI loads

If all three pass, you're ready for Railway deployment.

---

## Phase A: Deploy to Railway (10-15 minutes)

### Step A1: Gather Required Credentials

Before opening Railway dashboard, collect these values locally:

| Variable | Source | Example |
|----------|--------|---------|
| `WHATSAPP_PROVIDER` | .env or choose | `meta` |
| `WHATSAPP_OWNER_NUMBER` | .env | `+62xxxxxxxxxx` |
| `META_PHONE_NUMBER_ID` | Meta for Developers → WhatsApp Business Account | `120xxxxxx` |
| `META_ACCESS_TOKEN` | Meta for Developers → System User → Token | `EAAxxxxxx` |
| `META_VERIFY_TOKEN` | You choose (random string) | `my-secret-1234` |
| `NOTION_API_TOKEN` | Notion → Integrations → Create → Token | `secret_xxxxx` |
| `NOTION_WORKFLOW_PARENT_ID` | Notion page UUID | `xxxxxxxxxxxxxxxx` |
| `GOOGLE_DRIVE_CREDENTIALS_JSON` | service_account.json minified | `{"type":"service_account",...}` |
| `OPENAI_API_KEY` | OpenAI API → Keys | (leave blank if not ready) |
| `ANTHROPIC_API_KEY` | Anthropic console → API keys | (leave blank if not ready) |

### Step A2: Log into Railway & Create Project

1. Go to [railway.app](https://railway.app)
2. Log in with your GitHub account
3. Click **New Project**
4. Select **Deploy from GitHub repo**
5. Authorize Railway to access your repos
6. Select `apsmono/solo-leveling`

Railway will scan and detect `Dockerfile` automatically.

### Step A3: Configure Build Settings

In the Railway project service settings:

1. **Source** tab:
   - Ensure GitHub repo is `apsmono/solo-leveling`
   - Branch: `main` (for production; we'll add `development` later)
   - Auto-deploy: enabled

2. **Builder** tab:
   - Set to **Dockerfile** (not Nixpacks)

3. **Deployment** tab:
   - Watch paths: `/` (so all code changes trigger redeploy)

### Step A4: Add Environment Variables

In the service **Variables** tab, add each variable individually (**do NOT upload .env file**):

```
WHATSAPP_PROVIDER=meta
WHATSAPP_OWNER_NUMBER=+62xxxxxxxxxx
META_PHONE_NUMBER_ID=<your-value>
META_ACCESS_TOKEN=<your-value>
META_VERIFY_TOKEN=<your-secret-value>
NOTION_API_TOKEN=<your-value>
NOTION_WORKFLOW_PARENT_ID=<your-value>
GOOGLE_DRIVE_CREDENTIALS_JSON=<minified-json>
GMAIL_ENABLED=false
AGENT_PROVIDER=openai
OPENAI_API_KEY=<blank-or-your-key>
ANTHROPIC_API_KEY=<blank-or-your-key>
REMINDER_STORE_PATH=data/reminders.json
SCHEDULER_POLL_SECONDS=30
DAILY_GMAIL_DIGEST_ENABLED=false
LIBRARY_MAINTENANCE_ENABLED=false
```

**Note on GOOGLE_DRIVE_CREDENTIALS_JSON:**
- Open your `service_account.json` file
- Remove all whitespace/newlines (minify to one line)
- Paste as the env var value
- Example: `{"type":"service_account","project_id":"xxx",...}`

### Step A5: Trigger First Deploy

1. Click **Deployments** tab
2. Click **Deploy** (or push a commit to `main`)
3. Watch the build logs

**Expected logs:**
```
[1/5] Building...
[2/5] Running Dockerfile...
[3/5] Starting container...
Application startup complete
```

Once you see "Application startup complete", note your public URL from the Railway dashboard:
```
https://<your-project-name>.up.railway.app
```

**Typical wait time:** 2-5 minutes for build + startup

---

## Phase B: Verify Health on Railway (5 minutes)

Once deployment is complete and you have your Railway URL, follow these tests in order:

### Test B1: FastAPI Docs Endpoint

```bash
# Replace <your-railway-url> with your actual Railway public URL
curl https://<your-railway-url>/docs
```

**Expected:** HTTP 200, HTML page loads

If you get `Connection refused` or `502 Bad Gateway`, the container is still starting. Wait 30 seconds and retry.

### Test B2: Health Check via Direct Webhook POST

```bash
# Simulate a WhatsApp message requesting "health"
curl -X POST https://<your-railway-url>/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -D '{
    "entry": [
      {
        "changes": [
          {
            "value": {
              "messages": [
                {
                  "from": "<WHATSAPP_OWNER_NUMBER>",
                  "text": {
                    "body": "health"
                  }
                }
              ]
            }
          }
        ]
      }
    ]
  }'
```

Or use a simpler approach — send the actual WhatsApp message from your phone.

### Test B3: Send WhatsApp Message (Easiest)

1. From your phone, send a WhatsApp message to your verified number
2. Type: `health`
3. Wait 5-10 seconds for response

**Expected response:**
```
System health check:

✅ Notion (NOTION_API_TOKEN set)
✅ Google Drive (GOOGLE_DRIVE_CREDENTIALS_JSON set)
✅ Gmail (disabled)
❌ OpenAI (missing: OPENAI_API_KEY)
❌ Anthropic (missing: ANTHROPIC_API_KEY)
✅ WhatsApp (Meta) (META_ACCESS_TOKEN, META_VERIFY_TOKEN, META_PHONE_NUMBER_ID set)

All integrations configured.
```

**If no response:**
- Check Railway logs: Deployments → [Latest] → Logs
- Look for error messages or "Intent detected: health"
- Verify `META_VERIFY_TOKEN` is set correctly in Railway
- Verify `WHATSAPP_OWNER_NUMBER` matches the phone sending the message

### Test B4: Status Command (Quick Liveness Check)

Send another WhatsApp message: `status`

**Expected response:** `Brain is online and listening.`

This confirms the webhook is receiving, routing, and sending messages.

---

## Phase C: Setup Persistence Volumes (10 minutes)

Railway resets the container filesystem on every redeploy. Without volumes, your library and reminders are lost.

### Step C1: Create Data Volume

1. In Railway service → **Volumes** tab
2. Click **Create Volume**
3. Set mount path: `/app/data`
4. Click **Create**

### Step C2: Create Library Volume

1. Click **Create Volume** again
2. Set mount path: `/app/library`
3. Click **Create**

### Step C3: Redeploy to Mount Volumes

1. **Deployments** tab
2. Click **Redeploy** (or push a commit)
3. Wait for startup

### Step C4: Verify Persistence

1. Send a WhatsApp reminder command: `remind me in 10 minutes test persistence`
2. Wait for the container to start
3. Check that the reminder was created: `data/reminders.json` now exists
4. Trigger another redeploy (Redeploy button or push commit)
5. Check logs for "reminders.json exists" (proves volume persisted)

---

## Phase D: Meta Webhook Registration (5 minutes)

For WhatsApp messages to reach your Railway webhook, you must register the callback URL with Meta.

### Step D1: Get Your Callback URL

From Railway dashboard:
```
https://<your-project-name>.up.railway.app/webhook/whatsapp
```

### Step D2: Register with Meta

1. Log in to [Meta for Developers](https://developers.facebook.com/)
2. Go to your WhatsApp app
3. Navigate to **WhatsApp → Configuration**
4. Under **Webhook settings**, click **Edit**
5. Set:
   - **Callback URL:** `https://<your-railway-url>/webhook/whatsapp`
   - **Verify Token:** Must match `META_VERIFY_TOKEN` from Railway env vars
6. Click **Verify and Save**
7. Subscribe to **messages** webhook field

**Expected:** Meta confirms webhook registered ✅

---

## Phase E: Optional — Add Staging Deployment (development branch)

Once production is running, set up a staging environment from the `development` branch.

### Step E1: Create Second Service in Same Project

1. In Railway project, click **Create New Service**
2. Select GitHub repo `apsmono/solo-leveling`
3. Set branch to `development`
4. Configure same env vars (optional: set `GMAIL_ENABLED=true` to test Gmail)
5. Deploy

You'll have:
- **Production:** `https://<project>.up.railway.app` (from `main`)
- **Staging:** `https://<project-staging>.up.railway.app` (from `development`)

---

## Phase F: Final Checklist (Ongoing Operations)

- [ ] Code passes local tests
- [ ] Railway project created with main branch connected
- [ ] All env vars added to Railway
- [ ] First deploy successful (logs show "Application startup complete")
- [ ] `/docs` endpoint returns 200
- [ ] Health command works via WhatsApp
- [ ] Status command works via WhatsApp
- [ ] Volumes created and reminders/library persist across redeployment
- [ ] Meta webhook registered with correct callback URL and verify token
- [ ] (Optional) Staging service from development branch deployed
- [ ] Monthly spending cap set in Railway → Billing

---

## Troubleshooting During Deployment

| Issue | Cause | Fix |
|-------|-------|-----|
| Build hangs for >10 min | Dockerfile syntax or large layer | Check logs; rebuild |
| `Application startup complete` but `/docs` returns 502 | Port mismatch or startup error | Check logs for errors like import failures |
| WhatsApp messages not received | Callback URL or verify token wrong with Meta | Re-register webhook; verify exact token match |
| No response from health command | Webhook not reaching Railway or router error | Check Railway logs for "Intent detected" |
| Library/data lost after redeploy | Volumes not mounted | Create volumes, redeploy, check mount paths |
| "Connection refused" on `curl` | Container still starting or wrong URL | Wait 30s, verify URL is correct |

---

## Reference Documents

- [Railway Setup Runbook](docs/research/railway-setup-runbook-2026-04-23.md) — detailed deployment theory
- [Deployment Status](docs/DEPLOYMENT_STATUS.md) — checklist and credential inventory
- [Health Verification Guide](docs/RAILWAY_HEALTH_VERIFICATION.md) — testing health checks
- [AI Team Coordination](docs/ai-team-coordination.md#release-checklist-development--main-gate) — release workflow

---

## Next Steps After Deployment

1. ✅ Health check passes (all critical integrations ✅)
2. ✅ WhatsApp commands routed and responding
3. ⏭️ Test Stage 8 workflows (inbox → Notion, etc.)
4. ⏭️ Test Stage 9 library commands
5. ⏭️ Monitor Railway logs and set alerts
6. ⏭️ Set custom domain (after stabilization)

---

**Summary:** This workflow takes ~30-45 minutes total (mostly waiting for Railway deploys). Once complete, you have a production brain running live on Railway with persistent data and WhatsApp integration working end-to-end.
