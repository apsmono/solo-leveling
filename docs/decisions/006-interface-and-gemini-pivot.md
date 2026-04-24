# 006 — Interface Scope Pivot And Gemini-First AI Employee

## Status

Accepted

## Date

2026-04-24

## Scope

Project roadmap, architecture docs, runtime AI provider defaults, and setup guidance.

## Context

The current roadmap and documentation were centered around WhatsApp as the primary command interface and OpenAI/Anthropic as primary AI providers. This created avoidable dependency on a single messaging channel and did not match the desired operating direction for the AI employee model.

## Decision

1. Remove WhatsApp from the active big-plan critical path.
2. Keep WhatsApp as an optional legacy adapter (not a blocker for roadmap execution).
3. Set Gemini as the primary AI employee provider.
4. Keep OpenAI and Anthropic as optional fallbacks.

## Why

- Reduces delivery risk tied to external messaging provider setup.
- Keeps command-center architecture interface-agnostic.
- Aligns AI employee runtime with preferred provider direction.
- Preserves compatibility while simplifying defaults.

## Consequences

### Positive

- Faster plan execution without WhatsApp dependency.
- Clearer setup order (core integrations + Gemini first).
- Runtime defaults now match intended operational model.

### Trade-offs

- Legacy docs and test flows needed broad synchronization.
- WhatsApp integration remains in codebase but is no longer primary.

## Implementation Notes

- `AGENT_PROVIDER` default changed to `gemini`.
- New env vars: `GEMINI_API_KEY`, `GEMINI_MODEL`.
- Dispatcher now supports Gemini primary path with OpenAI/Anthropic fallbacks.
- Plan docs updated to treat WhatsApp as optional legacy adapter.
