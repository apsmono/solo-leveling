# Decision 002 — WhatsApp Implementation Approach

- **Date:** 2026-04-17 14-45-47
- **Status:** accepted
- **Scope:** WhatsApp command interface (Stage 2)

## Context

The command center requires a WhatsApp channel for receiving commands from the owner and sending results back. Two legitimate options exist: Meta WhatsApp Cloud API (official, free tier, direct) and Twilio WhatsApp API (managed, faster prototype, per-message cost). An unofficial automation approach was considered and rejected on security and reliability grounds.

## Decision

Use **Meta WhatsApp Cloud API** as the primary implementation. Use **Twilio** only as a temporary prototype layer if Meta verification takes too long to complete.

## Why

- Meta Cloud API is the official channel with no per-message cost on the free tier.
- Long-term stability is better on the official API than on a third-party managed service.
- Meta's webhook model fits the architecture cleanly: receive POST, parse intent, dispatch, respond.
- Twilio adds a dependency and cost that is unnecessary once the Meta integration is running.

## Alternatives Considered

- **Twilio only:** Faster setup but ongoing cost and an extra dependency layer.
- **WhatsApp Web automation (unofficial):** Rejected. Violates Terms of Service, fragile, and a security risk for a system that has write access to Notion, GDrive, and Gmail.

## Consequences

- Positive: no per-message cost, direct API ownership.
- Negative: Meta requires a Facebook Business account and phone number verification; this adds 1–3 days of setup time.
- Mitigation: scaffold the command handler so it works against a Twilio webhook temporarily and switches to Meta with a single environment variable change.
- Follow-up required: complete Meta Business verification before Stage 2 goes to production.

## Related Updates

- Documents updated: `docs/architecture/integrations.md`, `src/integrations/whatsapp/README.md`
- Changelog entry added: yes
- Next review date: when Meta verification is complete
