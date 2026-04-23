# Decision: Main Branch Semantic Version Tagging

- Title: Main Branch Semantic Version Tagging
- Date: `2026-04-23 17-06-51`
- Status: accepted
- Scope: Release workflow, version traceability, multi-AI operational governance

## Context

The repository has a formal `development -> main` release flow and CI coverage, but no durable release identity on `main`. Commit history alone is too low-level for cross-device and cross-AI release tracking.

## Decision

Adopt annotated semantic version tags on `main` releases using the format `vMAJOR.MINOR.PATCH`. Create and push the tag immediately after each release merge from `development` to `main`.

## Why

- Reason: Tags provide stable release anchors for operators and AI agents.
- Reason: SemVer communicates release impact clearly (breaking, feature, patch).
- Reason: Annotated tags preserve release intent in addition to commit provenance.

## Alternatives Considered

- Alternative: Use only git commit history and merge commits.
- Why not chosen: Harder to identify release boundaries quickly, especially across multiple AI sessions and devices.

## Consequences

- Positive consequence: Faster release identification and rollback targeting.
- Positive consequence: Better alignment between changelog summaries and deployable release points.
- Negative consequence: Adds one required release step (create/push tag).
- Follow-up required: Enforce checklist usage in release operations and keep bump rules consistent.

## Related Updates

- Documents updated: `docs/ai-team-coordination.md`, `docs/ai-knowledge/conventions.md`
- Changelog entry added: yes (`CHANGELOG.md`, 2026-04-23 17-06-51)
- Next review date: `2026-05-23`
