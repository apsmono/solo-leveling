# Railway Deployment Status

**Last Updated:** 2026-04-23
**Status:** Ready for staging deploy (development branch) and production deploy (main branch)

---

## Repository Readiness

| Check | Status | Notes |
|-------|--------|-------|
| Code on main branch | ✅ | Commit 57a2b5e: inline credential support + Railway Dockerfile fix |
| Code on development branch | ✅ | Commit 0746f0f: formalized workflow + release checklist |
| CI pipeline wired | ✅ | .github/workflows/ci.yml runs on [development, main] |
| Dockerfile Railway-compatible | ✅ | VOLUME directive removed (banned by Railway) |
| Tests passing locally | ✅ | 37 tests, 3 skipped, 0 failures |
| Inline credential loaders | ✅ | GOOGLE_DRIVE_CREDENTIALS_JSON, GMAIL_CREDENTIALS_JSON in place |
| Feature flags working | ✅ | GMAIL_ENABLED=false disables Gmail routes |

---

## Deployment Checklist

### Phase 1: Railway Project Setup (Manual in Dashboard)

- [ ] Log in to railway.com
- [ ] Create new project
- [ ] Connect solo-leveling GitHub repo
- [ ] Verify Dockerfile detected as builder
- [ ] Set Watch Paths to `/` for auto-redeploy

### Phase 2: Environment Variables (Manual Entry in Railway)

Set these variables in Railway dashboard:

```
WHATSAPP_PROVIDER=meta
WHATSAPP_OWNER_NUMBER=+62xxxxxxxxxx
META_PHONE_NUMBER_ID=<value>
META_ACCESS_TOKEN=<value>
META_VERIFY_TOKEN=<secret>
NOTION_API_TOKEN=<value>
NOTION_WORKFLOW_PARENT_ID=<value>
GOOGLE_DRIVE_CREDENTIALS_JSON=<minified JSON>
GMAIL_ENABLED=false
AGENT_PROVIDER=openai
OPENAI_API_KEY=<value when ready>
ANTHROPIC_API_KEY=<value when ready>
REMINDER_STORE_PATH=data/reminders.json
SCHEDULER_POLL_SECONDS=30
DAILY_GMAIL_DIGEST_ENABLED=false
LIBRARY_MAINTENANCE_ENABLED=false
```

Note: `GOOGLE_DRIVE_CREDENTIALS_JSON` should be the entire service account JSON minified to one line (no line breaks).

### Phase 3: First Deploy

For **staging** (development branch):
1. In Railway dashboard, add a service
2. Set branch to `development`
3. Trigger deploy
4. Wait for startup complete in logs
5. Record the public URL: `https://<project>.up.railway.app`

For **production** (main branch):
1. Create a second service in same project
2. Set branch to `main`
3. Environment variables: same as staging (plus GMAIL_ENABLED=true if ready)
4. Trigger deploy
5. Record the public URL: `https://<project-prod>.up.railway.app`

### Phase 4: Verification

For each service:
- [ ] Health check: `curl https://<url>/docs` returns 200
- [ ] Check logs: no crash, "Application startup complete" visible
- [ ] WhatsApp test: send "health" command, receive status report

### Phase 5: Meta Webhook Registration

1. Log in to Meta for Developers → WhatsApp app
2. Go to Configuration
3. Set Callback URL: `https://<staging-url>/webhook/whatsapp`
4. Set Verify Token: match `META_VERIFY_TOKEN` from Railway
5. Subscribe to **messages** field
6. Test: send WhatsApp message, verify it reaches webhook logs

### Phase 6: Persistence Setup (Volumes)

In Railway dashboard for each service:
1. Create volume, mount at `/app/data` (reminders persistence)
2. Create volume, mount at `/app/library` (library persistence)
3. Redeploy
4. Verify by checking that reminders/library survive a redeploy

### Phase 7: Operations

- [ ] Set monthly spending cap in Railway → Billing
- [ ] Enable log alerts
- [ ] Register custom domain (optional, for stability)
- [ ] Document final URLs in team notes

---

## Key Credentials Still Needed

Before you can start Phase 1, gather these from your local environment:

1. **Meta/WhatsApp:**
   - `META_PHONE_NUMBER_ID` (WhatsApp Business Account)
   - `META_ACCESS_TOKEN` (WhatsApp API)
   - `META_VERIFY_TOKEN` (custom string you choose)

2. **Google Drive:**
   - Service account JSON file (or env var already set locally)

3. **Notion:**
   - `NOTION_API_TOKEN`
   - `NOTION_WORKFLOW_PARENT_ID` (Notion page UUID)

4. **AI Agents:**
   - `OPENAI_API_KEY` (optional, can leave blank initially)
   - `ANTHROPIC_API_KEY` (optional, can leave blank initially)

---

## Decision: Staging vs Production Approach

**Recommended:**
1. Deploy `development` branch to Railway **staging** service first
2. Test WhatsApp commands end-to-end with GMAIL_ENABLED=false
3. After staging validation, merge `development` → `main` via release PR
4. Deploy `main` to Railway **production** service
5. Enable GMAIL_ENABLED=true in production only (when ready)

This matches the governance model formalized in `docs/ai-team-coordination.md`.

---

## Links

- Runbook: [docs/research/railway-setup-runbook-2026-04-23.md](docs/research/railway-setup-runbook-2026-04-23.md)
- Branch workflow: [docs/ai-team-coordination.md#release-checklist-development--main-gate](docs/ai-team-coordination.md#release-checklist-development--main-gate)
- Governance: [docs/ai-employer-operating-system.md](docs/ai-employer-operating-system.md)
