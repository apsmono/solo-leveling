# Decision Record 004: Research Recording and Approval Gate

- Title: Research recording requirement and explicit approval gate before policy execution
- Date: 2026-04-23 10-33-27
- Status: accepted
- Scope: AI workflow governance, policy update process, and research traceability

## Context

The owner requested strict process controls for AI sessions:

- Postpone ongoing work when policy-level changes are proposed.
- Present update suggestions and reasons first.
- Continue only after explicit owner approval.
- Record each research output and decision in repository documentation.

The repository already emphasizes documentation-first operation but did not define this exact approval gate as a formal decision.

## Decision

Adopt a mandatory Approval Gate and Research Recording Protocol:

1. Policy or governance updates must pause normal execution until explicit owner approval is provided.
2. All substantial research outputs must be stored as durable files under `docs/research/`.
3. Every accepted policy/governance update must be captured in decision records and changelog entries.

## Why

- Enforces owner control for governance-level changes.
- Preserves cross-device continuity and avoids knowledge loss.
- Improves auditability of AI behavior and strategic decisions.

## Alternatives Considered

- Alternative: Keep research in chat only.
- Why not chosen: Loses durable history and weakens traceability across devices and agents.

- Alternative: Auto-apply policy updates without explicit owner approval.
- Why not chosen: Conflicts with owner-defined decision gate and increases governance risk.

## Consequences

- Positive consequence: Better control, transparency, and repeatability of AI-driven changes.
- Negative consequence: Slightly slower execution due to explicit gate steps.
- Follow-up required: Keep policy files and operational docs synchronized with this gate.

## Related Updates

- Documents updated: `AGENTS.md`, `.github/copilot-instructions.md`, `docs/README.md`, `docs/ai-working-notes.md`, `docs/research/ai-key-providers-2026-04-23.md`, `docs/research/deployment-hosting-2026-04-23.md`
- Changelog entry added: Yes
- Next review date: 2026-05-23
