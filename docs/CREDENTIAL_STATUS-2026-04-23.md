# Credential Setup Status — 2026-04-23

## Status Summary

**Overall:** 70% Complete. Core integrations (Notion, Google Drive, Gmail) are configured. WhatsApp and AI provider keys still needed.

---

## Credential Inventory

### ✅ CONFIGURED (Ready to Test)

#### Notion
- **NOTION_API_TOKEN:** ✅ SET (`ntn_bb5538...`)
  - **User question answered:** "Notion API token" = "Notion API key" — they're the same thing. You used the correct variable name.
- **NOTION_WORKFLOW_PARENT_ID:** ✅ SET (`345021028cc88...`)
  - **Great find!** This was marked as blocking TODO. You've unlocked Stage 8 workflow outputs.

#### Google Drive
- **GOOGLE_DRIVE_CREDENTIALS_PATH:** ✅ SET (`./.credentials/google/service_account.json`)
- **GOOGLE_DRIVE_CREDENTIALS_JSON:** ✅ SET (base64 encoded)
- **Status:** Ready to read/write Google Drive files

#### Gmail
- **GMAIL_CREDENTIALS_PATH:** ✅ SET (`./.credentials/google/client_secret_...json`)
- **GMAIL_CREDENTIALS_JSON:** ✅ SET (base64 encoded)
- **GMAIL_TOKEN_PATH:** ✅ SET (`.gmail_token.json`)
- **Status:** Ready (first call will trigger OAuth consent flow)
- **Note:** `GMAIL_ENABLED=false` in .env — Gmail is currently disabled. Change to `true` to enable.

#### WhatsApp (Meta) — Partial
- **META_ACCESS_TOKEN:** ✅ SET (`1640362067209385`)
- **META_PHONE_NUMBER_ID:** ❌ MISSING
- **META_VERIFY_TOKEN:** ❌ MISSING
- **Status:** BLOCKING — cannot receive/verify WhatsApp messages without these

---

## ❌ NOT CONFIGURED (Blocking)

### WhatsApp
- Missing: `META_PHONE_NUMBER_ID`, `META_VERIFY_TOKEN`
- **Impact:** WhatsApp webhook cannot verify incoming requests or send messages
- **Action:** Get these from Meta Developers dashboard (WhatsApp > Settings > Business Account)

### AI Provider
- **OPENAI_API_KEY:** ❌ MISSING
- **ANTHROPIC_API_KEY:** ❌ MISSING
- **Impact:** `ask` command cannot run; AI dispatch will fail
- **Action:** Choose one:
  - OpenAI: Get key from `platform.openai.com/account/api-keys`
  - Anthropic: Get key from `console.anthropic.com`

---

## What You Can Test Now

### 1. **Notion Integration** ✅
```bash
# Test Notion connectivity
python3 -c "from src.integrations.notion.client import NotionClient; c = NotionClient(); print(c.get_database_title('test'))"
```

### 2. **Google Drive + Gmail** ✅ (Gmail requires GMAIL_ENABLED=true)
```bash
# List Google Drive files
python3 << 'EOF'
from src.integrations.gdrive.client import GoogleDriveClient
from src.integrations.gmail.client import GmailClient

# Test Drive
drive = GoogleDriveClient()
print("Drive ready:", drive is not None)

# Test Gmail (requires GMAIL_ENABLED=true and will prompt for OAuth on first run)
gmail = GmailClient()
print("Gmail ready:", gmail is not None)
EOF
```

### 3. **Full Test Suite**
```bash
# Run all tests (37 tests, 3 skipped for live features)
python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v
```

---

## What Still Blocks WhatsApp

To receive commands from WhatsApp and test end-to-end:

1. **Get missing Meta credentials:**
   - `META_PHONE_NUMBER_ID` — your WhatsApp Business Account phone number ID (find in Meta Developers dashboard)
   - `META_VERIFY_TOKEN` — a custom verification string you create (any random string, e.g., `my_verify_secret`)

2. **Test webhook locally:**
   ```bash
   uvicorn src.integrations.whatsapp.handler:app --port 8000
   ```

3. **Expose with ngrok:**
   ```bash
   ngrok http 8000
   ```

4. **Configure in Meta Developers:**
   - Callback URL: `https://<ngrok-url>/whatsapp/webhook`
   - Verify Token: (the value you set in .env)

---

## Recommended Next Steps

### Immediate (10 min):
1. [ ] Get `META_PHONE_NUMBER_ID` and `META_VERIFY_TOKEN` from Meta Developers dashboard
2. [ ] Choose AI provider and get API key (OpenAI or Anthropic)
3. [ ] Set `GMAIL_ENABLED=true` in .env

### Then Test (20 min):
1. [ ] Run test suite: `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v`
2. [ ] Test with health check (once all credentials set)
3. [ ] Manual WhatsApp test: send `status` from owner number

### Deployment Ready (after credentials):
- All services tested ✓
- Railway auto-deploys on main push ✓
- CI pipeline validates changes ✓

---

## Notes

- **Google backward compatibility:** You have both `GOOGLE_DRIVE_CREDENTIALS_PATH/JSON` and legacy `GOOGLE_CREDENTIALS_PATH/JSON` set. The split versions take precedence; legacy fallback still works.
- **Gmail OAuth:** First call will open a browser for consent and cache the token in `.gmail_token.json`. Keep this file locally (git-ignored).
- **Credentials in Railway:** Use `GOOGLE_DRIVE_CREDENTIALS_JSON` and `GMAIL_CREDENTIALS_JSON` (base64) for Railway deployment — file paths won't work there.

