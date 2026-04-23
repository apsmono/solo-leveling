# AI Installation Guide

## Goal

Use this guide to make another repository AI-friendly in the same way as this workspace: explicit instructions, reusable prompts, and clear documentation for long-term AI collaboration.

## Research Conclusion: Git Log vs Better Change Record

Short answer: do not use git commit messages as the only change record for AI.

Best practice is a layered model:

1. Git commits for atomic code provenance
2. `CHANGELOG.md` for curated human and AI-readable impact history
3. Session/continuity notes for in-progress context and handoff
4. Decision records for major policy or architecture choices

Why this is better than git log alone:

- Commit messages are implementation-first and can be noisy, inconsistent, or split across many commits.
- AI agents need stable, semantic summaries of impact, not just low-level commit diffs.
- Curated changelog entries and decision records reduce re-discovery cost across devices and across AI tools.

Recommended default rule: treat git history as raw evidence and `CHANGELOG.md` as the canonical operational record.

## Files To Create

Replicate these files in the target repository:

- `README.md`
- `AGENTS.md`
- `AI_CONTEXT.md`
- `CHANGELOG.md`
- `docs/AI_CHANGELOG_POLICY.md`
- `.github/copilot-instructions.md`
- `.vscode/extensions.json`
- `.vscode/settings.json`
- `prompts/ai-friendly-workspace.prompt.md`

## Setup Principles

- Start from the real project goal, not a generic template.
- Give AI tools a small number of authoritative files.
- Keep instructions synchronized with the repository as it evolves.
- Prefer actionable structure over long narrative descriptions.
- Treat changelog maintenance as part of the implementation, not as optional cleanup.
- Use local device time with the format `YYYY-MM-DD HH-mm-ss` for changelog entries.
- Use a layered change-record stack: commit history + curated changelog + continuity notes + decisions.

## AI-Friendly Change Record Structure

Use these files as a minimal, scalable standard:

- `CHANGELOG.md` (required): notable, curated, human-readable project history.
- `docs/ai-working-notes.md` (recommended): cross-session AI memory, troubleshooting, and handoff notes.
- `docs/decisions/NNN-*.md` (required for major decisions): architectural, policy, or process decisions.
- Git commit log (required): atomic implementation provenance.

If only one file can be maintained, maintain `CHANGELOG.md`. If two can be maintained, add `docs/ai-working-notes.md`.

## Read / Write Protocol For AI Agents

### Read Before Work (minimum)

Before making changes, AI agents should read:

1. `README.md`
2. `AGENTS.md`
3. `AI_CONTEXT.md`
4. `CHANGELOG.md` (latest active section)
5. Active task documents relevant to the requested change

### Write After Work (minimum)

After notable changes, AI agents should update in the same change set:

1. `CHANGELOG.md` with timestamped impact entry
2. Any documentation whose meaning or usage changed
3. `docs/ai-working-notes.md` when session findings affect future work
4. `docs/decisions/NNN-*.md` when a significant policy or architecture decision was made

### Entry Quality Rules

- Write for fast human scanning and AI retrieval.
- Record impact and behavior change, not only implementation details.
- Keep each changelog item concise and specific.
- Do not dump raw commit messages into changelog entries.
- Prefer one meaningful entry over many tiny noisy entries.

## Suggested Changelog Entry Template

```md
## Unreleased

### Changed

- 2026-04-23 13-00-00 Updated webhook auth flow so unauthorized requests return 403 with clearer operator guidance; reduces debugging time during deployment checks.
```

## Suggested Commit + Changelog Pairing

- Commit message answers: what changed in code/docs
- Changelog entry answers: why it matters operationally

Example:

- Commit: `feat(router): add provider-aware WhatsApp health checks`
- Changelog: `Added provider-specific health validation for WhatsApp (Meta vs Twilio), preventing false-ready setup states during onboarding.`

## Reusable Prompt

Use the following prompt with GitHub Copilot or another coding agent inside a new repository:

```md
Initiate this workspace to be AI-friendly.

Create a lightweight AI collaboration scaffold that includes:

- `README.md` updated with an AI workspace section
- `AGENTS.md` with repository-wide agent instructions
- `AI_CONTEXT.md` with project intent, current phase, source-of-truth files, growth conventions, and collaboration rules
- `CHANGELOG.md` with a human-readable changelog template
- `docs/AI_CHANGELOG_POLICY.md` defining scalable changelog rules and timestamp format
- `.github/copilot-instructions.md` with GitHub Copilot-specific guidance
- `.vscode/extensions.json` with minimal AI and documentation extension recommendations
- `.vscode/settings.json` with conservative workspace settings that help documentation and AI-assisted work
- `AI_INSTALLATION.md` explaining the setup and how to reproduce it later
- `prompts/ai-friendly-workspace.prompt.md` containing the reusable bootstrap prompt

Requirements:

- Keep the scaffold minimal and project-focused.
- Base all documentation on the actual purpose and current state of the repository.
- Avoid filler, speculative roadmap content, and unsupported technical assumptions.
- Make the AI-facing files work both now and as the project grows.
- Add instructions that AI must update changelog, documentation, and short descriptions whenever relevant changes are made.
- Use local device time in the format `YYYY-MM-DD HH-mm-ss` for changelog entries.
- Update existing files instead of replacing project intent.
- If the repository is early-stage, optimize for documentation-first collaboration.
- Add explicit read-before-work and write-after-work rules so different AI tools maintain consistent context quality.
```

## Maintenance Rule

Whenever the target repository adds code, environments, automations, or deployment workflows, update the AI-facing files in the same change so future AI tasks operate against current reality.

## Quick Adoption Checklist

- [ ] `CHANGELOG.md` exists with timestamped, curated entries
- [ ] `docs/ai-working-notes.md` exists for cross-session continuity
- [ ] AI instructions enforce read-before-work and write-after-work
- [ ] Major decisions are stored in `docs/decisions/`
- [ ] AI prompt includes change-record maintenance requirements
