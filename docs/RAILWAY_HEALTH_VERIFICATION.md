# Railway Health Verification Guide

**Date:** 2026-04-23
**Status:** Testing before deployment

---

## What the Health Check Does

The `health` command performs a **non-destructive audit** of your environment variables and returns a structured report of which integrations are configured and which are missing credentials.

**Trigger words (WhatsApp or any interface):**
- `health`
- `check setup`
- `system health`
- `integration status`

---

## Local Testing (Before Railway Deployment)

### Step 1: Start the server locally

```bash
cd /Users/macmini/Documents/projects/solo-leveling
.venv/bin/python -m uvicorn src.integrations.whatsapp.handler:app --port 8000
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
Application startup complete
```

### Step 2: Verify FastAPI documentation endpoint

In a new terminal:
```bash
curl http://localhost:8000/docs
```

Expected response:
- **HTTP 200** with HTML FastAPI Swagger UI page
- Confirms the webhook server is running

### Step 3: Test health command via Python (without WhatsApp)

```bash
# In a new terminal, same repo directory:
python3 -c "
from src.core.router import route_command
result = route_command('health')
print(result)
"
```

**Expected output format:**
```
System health check:

✅ Notion (NOTION_API_TOKEN set)
✅ Google Drive (GOOGLE_DRIVE_CREDENTIALS_PATH set)
✅ Gmail (GMAIL_CREDENTIALS_JSON set)
❌ OpenAI (missing: OPENAI_API_KEY)
❌ Anthropic (missing: ANTHROPIC_API_KEY)
✅ WhatsApp (Meta) (META_ACCESS_TOKEN, META_VERIFY_TOKEN, META_PHONE_NUMBER_ID set)

All integrations configured.
```

If any are missing:
```
System health check:

✅ Notion (NOTION_API_TOKEN set)
❌ Google Drive (missing: GOOGLE_DRIVE_CREDENTIALS_PATH)
✅ Gmail (disabled)
❌ OpenAI (missing: OPENAI_API_KEY)
❌ Anthropic (missing: ANTHROPIC_API_KEY)
❌ WhatsApp (Meta) (missing: META_PHONE_NUMBER_ID, META_ACCESS_TOKEN)

Missing credentials: GOOGLE_DRIVE_CREDENTIALS_PATH, OPENAI_API_KEY, ANTHROPIC_API_KEY, META_PHONE_NUMBER_ID, META_ACCESS_TOKEN
See docs/SETUP_SECRETS.md to configure them.
```

---

## Integration Status Breakdown

| Status | What It Means | Action If Missing |
|--------|---------------|-------------------|
| ✅ Notion | NOTION_API_TOKEN is set | Required for Stage 8 workflows; set in .env or Railway Variables |
| ✅ Google Drive | Drive credentials available (path or inline JSON) | Required for workflow output export; set GOOGLE_DRIVE_CREDENTIALS_PATH or GOOGLE_DRIVE_CREDENTIALS_JSON |
| ✅ Gmail | Gmail credentials available OR disabled flag is set | Set GMAIL_CREDENTIALS_JSON or keep GMAIL_ENABLED=false; optional until Email workflows needed |
| ✅ OpenAI | OPENAI_API_KEY is set | Required for "ask AI" commands; optional to leave blank initially |
| ✅ Anthropic | ANTHROPIC_API_KEY is set | Required for Anthropic model; optional to leave blank initially |
| ✅ WhatsApp (Meta) | All Meta webhook credentials set | **Critical** — required for WhatsApp to work |
| ✅ WhatsApp (Twilio) | All Twilio credentials set | Alternative to Meta; only if WHATSAPP_PROVIDER=twilio |

**Critical integrations:** WhatsApp + Notion + at least one AI provider (OpenAI or Anthropic)

**Optional until workflows enabled:** Gmail (set GMAIL_ENABLED=false to disable), Drive export, Anthropic

---

## Pre-Railway Health Checklist

Before deploying to Railway, run through these checks:

### Phase 1: Local Validation

- [ ] Start server: `uvicorn src.integrations.whatsapp.handler:app --port 8000`
- [ ] FastAPI docs load: `curl http://localhost:8000/docs` → **HTTP 200**
- [ ] Health command works: `python3 -c "from src.core.router import route_command; print(route_command('health'))"`
- [ ] All critical integrations show ✅ (see breakdown above)
- [ ] No Python errors in startup logs

### Phase 2: Status Command

Test the "status" command to verify routing is working:

```bash
python3 -c "
from src.core.router import route_command
print(route_command('status'))
"
```

Expected output:
```
Brain is online and listening.
```

### Phase 3: Full Test Suite

Before Railway deployment, ensure unit tests pass:

```bash
cd /Users/macmini/Documents/projects/solo-leveling
.venv/bin/python -m unittest discover -v
```

Expected result:
```
Ran 37 tests in 0.236s
OK (skipped=3)
```

### Phase 4: Prepare Railway Environment Variables

Gather this information (from `.env.example` and your local setup):

**Minimal Railway config (required):**
```
WHATSAPP_PROVIDER=meta
WHATSAPP_OWNER_NUMBER=+62xxxxxxxxxx
META_PHONE_NUMBER_ID=<value>
META_ACCESS_TOKEN=<value>
META_VERIFY_TOKEN=<value>
NOTION_API_TOKEN=<value>
NOTION_WORKFLOW_PARENT_ID=<page-uuid>
GOOGLE_DRIVE_CREDENTIALS_JSON=<minified-json>
GMAIL_ENABLED=false
AGENT_PROVIDER=openai
OPENAI_API_KEY=<key-or-leave-blank>
ANTHROPIC_API_KEY=<key-or-leave-blank>
```

**Optional Railway config:**
```
REMINDER_STORE_PATH=data/reminders.json
SCHEDULER_POLL_SECONDS=30
DAILY_GMAIL_DIGEST_ENABLED=false
LIBRARY_MAINTENANCE_ENABLED=false
```

---

## Testing on Railway (Post-Deploy)

Once deployed to Railway, use these commands to verify health:

### Test 1: FastAPI docs endpoint

```bash
curl https://<your-railway-url>/docs
# Expected: HTTP 200, Swagger UI loads
```

### Test 2: Health command via WhatsApp

Send a WhatsApp message to your verified number with text: `health`

Expected flow:
1. Meta webhook receives message
2. Webhook → POST to Railway `/webhook/whatsapp`
3. Router detects "health" intent
4. Health handler runs the audit
5. Response routed back via WhatsApp API
6. You receive the health report in WhatsApp

### Test 3: Status command via WhatsApp

Send: `status`

Expected response: `Brain is online and listening.`

---

## Common Issues And Troubleshooting

### Issue: Health check shows many ❌ (missing integrations)

**Action:** Review which are critical:
- **WhatsApp required** → set META_* vars before deploying
- **Notion required** → set NOTION_API_TOKEN and NOTION_WORKFLOW_PARENT_ID
- **AI provider required** → set OPENAI_API_KEY or ANTHROPIC_API_KEY (or leave blank to skip initially)
- **Google Drive optional** → only needed for workflow export; set GOOGLE_DRIVE_CREDENTIALS_JSON if workflows use Drive
- **Gmail optional** → keep GMAIL_ENABLED=false unless actively using Email

### Issue: WhatsApp credential missing but .env has them

**Action:** Verify environment variable loading:
```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('META_ACCESS_TOKEN:', os.environ.get('META_ACCESS_TOKEN'))
print('META_PHONE_NUMBER_ID:', os.environ.get('META_PHONE_NUMBER_ID'))
"
```

If blank, `.env` is not being loaded. Check:
1. `.env` file exists in repo root
2. `from dotenv import load_dotenv; load_dotenv()` runs at startup (it does in `handler.py`)

### Issue: FastAPI docs return 500 or hang

Check server logs:
```bash
# Local: scroll terminal running uvicorn
# Railway: Railway dashboard → Deployments → Logs
```

Look for:
- Import errors (missing packages)
- Module not found (PYTHONPATH misconfiguration)
- Startup checks failing (directory creation errors)

### Issue: WhatsApp message sent but no response

Check:
1. **Webhook registered correctly?** — Meta dashboard → Configuration → Callback URL matches exactly
2. **Verify token correct?** — Callback URL verify token must match `META_VERIFY_TOKEN` in env vars
3. **Server logs show message received?** — Check Railway logs for "Intent detected"
4. **Send routing working?** — Check if `send_message()` is being called (requires `send_message()` to succeed)

---

## Reference: Health Check Source Code

The health check is defined in `src/core/router.py::_handle_health()`.

It audits:
- Environment variables for each integration
- File existence for optional tokens (e.g., `.gmail_token.json`)
- Feature flag state (GMAIL_ENABLED)

It does **not:**
- Make actual API calls to Notion, Drive, Gmail, etc.
- Require credentials to be functional, only present
- Test message sending or webhook connectivity (use WhatsApp command for that)

---

## Next Steps

1. ✅ Run local health check (`python3 -c "from src.core.router import route_command; print(route_command('health'))"`)
2. ✅ Verify test suite passes (`python -m unittest discover -v`)
3. ⏭️ Deploy to Railway (follow [docs/DEPLOYMENT_STATUS.md](docs/DEPLOYMENT_STATUS.md))
4. ⏭️ Test health and status commands via WhatsApp on Railway
5. ⏭️ Create volumes for library and reminder persistence
