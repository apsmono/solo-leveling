# Security Rules

Non-negotiable security constraints for this repository.
These must never be relaxed without a new formal decision record in `docs/decisions/`.

1. **No credentials in the repo.** All secrets go in `.env` (never committed). `.env` is in `.gitignore`.

2. **`.gmail_token.json` is in `.gitignore`.** It grants full inbox read access. It must never be committed or shared.

3. **WhatsApp owner-number guard.** `src/integrations/whatsapp/handler.py` checks `message["from"]` against `WHATSAPP_OWNER_NUMBER` before routing any command. Messages from other numbers are silently ignored. Do not remove or weaken this check.

4. **Read-only first.** Every integration was written read-only first. Write access was added only where the use case explicitly required it (Notion page creation, Google Doc creation). Gmail write (send/draft) was intentionally excluded from Stage 5.

5. **No destructive actions without explicit confirmation.** The brain must never delete Notion content, Drive files, or emails without an explicit user confirmation step built into the workflow.

6. **Environment variables must fail loudly.** `src/core/config.py` raises `EnvironmentError` when a required variable is missing. It must never fall back to an empty string or a default that silently disables a security feature.
