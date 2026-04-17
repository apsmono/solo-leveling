# AI Installation Guide

## Goal

Use this guide to make another repository AI-friendly in the same way as this workspace: explicit instructions, reusable prompts, and clear documentation for long-term AI collaboration.

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
```

## Maintenance Rule

Whenever the target repository adds code, environments, automations, or deployment workflows, update the AI-facing files in the same change so future AI tasks operate against current reality.
