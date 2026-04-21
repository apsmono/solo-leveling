# Task MULTI-AI-002 Research: Integration Smoke Coverage

## Scope Audited

- Router entry points in `src/core/router.py`
- Workflow composition in `src/core/workflows.py`
- Integration clients in `src/integrations/notion/client.py`, `src/integrations/gdrive/client.py`, `src/integrations/gmail/client.py`, and `src/integrations/whatsapp/handler.py`
- Existing test surface in `tests/`

## Findings

1. The repo has strong Stage 9 filesystem tests but no cross-integration smoke suite yet.
2. Router dispatch is the highest-value smoke surface because it exercises the user-facing command contract without needing full webhook setup.
3. Live integrations have different credential requirements and cannot all be exercised on every machine.
4. WhatsApp end-to-end verification is intentionally out of scope for smoke tests because it requires a public HTTPS webhook.

## Credential Reality

1. Notion live smoke only needs `NOTION_API_TOKEN`.
2. Google Drive live smoke currently expects `GOOGLE_CREDENTIALS_PATH` to point to a service-account JSON because `src/integrations/gdrive/client.py` uses `service_account.Credentials.from_service_account_file()`.
3. Gmail live smoke expects OAuth credentials or an already-created token cache because `src/integrations/gmail/client.py` uses `InstalledAppFlow` and `Credentials.from_authorized_user_file()`.
4. This means the current shared `GOOGLE_CREDENTIALS_PATH` variable serves two different credential modes across Drive and Gmail. The smoke suite should surface this clearly instead of hiding it.

## Recommended Smoke Matrix

### No-Credential Safe

1. Router `status`
2. Router `notion <query>` with mocked Notion client
3. Router `drive` with mocked Drive client
4. Router `email` with mocked Gmail client
5. Router `ask <question>` with mocked AI dispatcher
6. Workflow guardrail when `NOTION_WORKFLOW_PARENT_ID` is missing
7. AI dispatch guardrail when API key is missing
8. WhatsApp payload extraction helper

### Live Optional

1. Notion search if `NOTION_API_TOKEN` exists
2. Drive list if `GOOGLE_CREDENTIALS_PATH` points to a service-account JSON
3. Gmail unread list if OAuth client credentials or an existing Gmail token cache is available

## Implementation Decision

1. Keep the smoke suite in `unittest` to match the existing test style and avoid adding new mandatory dependencies.
2. Use explicit `skipTest()` messages for missing credentials so local runs remain informative.
3. Treat the Drive/Gmail credential split as a documented limitation for now rather than widening scope into auth refactoring during this task.
