# Secrets And Service Setup TODO

This file is your setup checklist for local development.
Right now, this project has no configured credentials, so live integrations are expected to fail until this is completed.

## Status

- Current state: **Not configured**
- Blocking impact: Notion, Gmail, Google Drive, WhatsApp send/receive, and AI agents cannot run end-to-end.

## Step 1: Prepare local environment file

1. Copy `.env.example` to `.env`.
2. Keep `.env` local only. Never commit it.
3. Fill values gradually and test each service one by one.

## Step 2: WhatsApp (Meta preferred)

Required keys in `.env`:

- `WHATSAPP_PROVIDER=meta`
- `WHATSAPP_OWNER_NUMBER`
- `META_PHONE_NUMBER_ID`
- `META_ACCESS_TOKEN`
- `META_VERIFY_TOKEN`

Verification:

1. Run `uvicorn src.integrations.whatsapp.handler:app --port 8000`
2. Expose with ngrok and configure webhook URL in Meta.
3. Send `status` from your owner number.

## Step 3: Notion

Required keys:

- `NOTION_API_TOKEN`
- `NOTION_WORKFLOW_PARENT_ID` (for Stage 8 workflow output pages)

How to get `NOTION_WORKFLOW_PARENT_ID`:

1. Open target Notion page in browser.
2. Copy page URL and take the 32-char page ID from the URL.
3. Share/invite your Notion integration to that page.

Verification:

1. Send `notion project` from WhatsApp.
2. Send `summarise my inbox and save to notion` (Stage 8 starter workflow).

## Step 4: Google Drive + Gmail

Required keys:

- `GOOGLE_CREDENTIALS_PATH`
- `GMAIL_TOKEN_PATH` (default `.gmail_token.json` is fine)

Notes:

- Gmail requires OAuth2 user credentials.
- First Gmail call opens browser consent flow and creates token cache.

Verification:

1. Send `email` and confirm summary returns.
2. Send `drive` and confirm file list returns.

## Step 5: AI provider

Choose one:

- OpenAI:
  - `AGENT_PROVIDER=openai`
  - `OPENAI_API_KEY`
  - optional `OPENAI_MODEL`
- Anthropic:
  - `AGENT_PROVIDER=anthropic`
  - `ANTHROPIC_API_KEY`
  - optional `ANTHROPIC_MODEL`

Verification:

1. Send `ask summarize my priorities for today`.

## Step 6: Scheduler (already implemented)

Optional keys:

- `REMINDER_STORE_PATH`
- `SCHEDULER_POLL_SECONDS`
- `DAILY_GMAIL_DIGEST_ENABLED`
- `DAILY_GMAIL_DIGEST_HOUR`
- `DAILY_GMAIL_DIGEST_MINUTE`

Verification:

1. Send `remind me in 1 minutes to test scheduler`.
2. Confirm callback reminder is delivered.

## Run order recommendation

1. WhatsApp
2. Notion
3. Gmail
4. Drive
5. AI agent
6. Workflow and scheduler

## Done checklist

- [ ] `.env` exists and is filled
- [ ] `status` works via WhatsApp
- [ ] `notion <query>` works
- [ ] `email` works
- [ ] `drive` works
- [ ] `ask <question>` works
- [ ] `summarise my inbox and save to notion` works
- [ ] reminder callback works
