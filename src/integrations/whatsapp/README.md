# WhatsApp Integration

Handles inbound commands from the owner via WhatsApp and sends responses back.

## Supported Providers

| Provider                | Status                         | Notes                                              |
| ----------------------- | ------------------------------ | -------------------------------------------------- |
| Meta WhatsApp Cloud API | Primary (pending verification) | Official, free tier, no per-message cost           |
| Twilio WhatsApp API     | Prototype fallback             | Faster setup; swap via `WHATSAPP_PROVIDER` env var |

## Environment Variables

Copy `.env.example` at the repo root and fill in the values for your chosen provider.

```
WHATSAPP_PROVIDER=meta          # or: twilio
WHATSAPP_OWNER_NUMBER=+628xxxxxxxxx   # your verified number; only this number is accepted

# Meta Cloud API
META_PHONE_NUMBER_ID=
META_ACCESS_TOKEN=
META_VERIFY_TOKEN=              # any string you choose; used to verify the webhook

# Twilio (fallback)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_NUMBER=
```

## How It Works

1. Meta (or Twilio) sends a POST to your webhook URL when a message arrives.
2. `handler.py` verifies the request, extracts the sender number and message text.
3. If the sender is not `WHATSAPP_OWNER_NUMBER`, the message is silently ignored.
4. The message text is passed to `src/core/router.py` for intent parsing and dispatch.
5. The response returned by the router is sent back via the WhatsApp API.

## Webhook Verification (Meta)

Meta sends a GET request to verify the webhook on setup. `handler.py` handles this automatically using `META_VERIFY_TOKEN`.

## Files

- `handler.py` — webhook entry point; validates requests; calls router; sends replies
- `client.py` — thin wrapper around the WhatsApp API (send message, send template)

## Setup Steps

1. Create a Meta Business account and a WhatsApp Business app.
2. Add a phone number and complete verification.
3. Generate a permanent access token.
4. Deploy `handler.py` behind a public HTTPS endpoint (or use ngrok for local testing).
5. Register the webhook URL in the Meta developer dashboard.
6. Set all environment variables and run a test message.
