# AI Working Notes

This file is the entry point for AI cross-session memory.
All detailed knowledge is split into focused files inside `docs/ai-knowledge/`.

## Index

| File                                                                           | Contents                                                                    |
| ------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| [`ai-knowledge/build-history.md`](ai-knowledge/build-history.md)               | How the repo was built, stage by stage, with completion status              |
| [`ai-knowledge/conventions.md`](ai-knowledge/conventions.md)                   | Changelog rules, documentation update obligations, file structure map       |
| [`ai-knowledge/error-log.md`](ai-knowledge/error-log.md)                       | Every error encountered with root cause, fix, and prevention rule           |
| [`ai-knowledge/integration-patterns.md`](ai-knowledge/integration-patterns.md) | Gotchas and working patterns for WhatsApp, Notion, Drive, Gmail, AI agents  |
| [`ai-knowledge/security-rules.md`](ai-knowledge/security-rules.md)             | Non-negotiable security constraints (credentials, guards, read-only policy) |
| [`ai-knowledge/continuation-plan.md`](ai-knowledge/continuation-plan.md)       | What is done, what is not, next steps, and environment variable reference   |

## How to use this folder

1. **Starting a new session?** Read `AI_CONTEXT.md`, then `AGENTS.md`, then `continuation-plan.md`.
2. **Hit an error?** Check `error-log.md` first; add a new entry if you solve something new.
3. **Adding an integration?** Read `integration-patterns.md` and `security-rules.md` before writing code.
4. **Finishing a session?** Update `continuation-plan.md` with what changed, then stamp `CHANGELOG.md`.

## Recent note

- 2026-04-20: Terminology pivot applied — in this repo, "library" now means local folder `library/` only. Stage 9 handlers were switched from Notion-backed capture/search to local markdown storage under `library/profile`, `library/terms`, `library/books`, `library/articles`, `library/thoughts`, and `library/references`.
- 2026-04-18: Implemented first Stage 9 code slice: created `src/core/libraries.py` and wired new router intents (`library_profile`, `library_term`, `library_book`, `library_article`, `library_thought`, `library_review`) so knowledge profile and library capture commands are now routable.
- 2026-04-18: Stage 9 runtime currently uses Notion page capture mode under `NOTION_WORKFLOW_PARENT_ID` for immediate operation; database-property writes are the next hardening step.
- 2026-04-18: Started implementation of multi-agent coordination model: standardized `agent/<agent-name>/<task-slug>/<stage-or-scope>` branches, PR-first merge guidance for overlapping work, task-claim ownership, and handoff checklist expectations.
- 2026-04-18: Expanded Stage 9 library design with MCP-aligned knowledge profile scope (skills, interests, domains, learning priorities, focus themes) and explicit sensitive-data exclusions.
- 2026-04-18: Added a standard git preflight rule before preparation/setup (`git fetch --all --prune && git status -sb`) in setup and conventions docs.
- 2026-04-18: Added a mandatory AI sync rule in `.github/copilot-instructions.md` and `AGENTS.md` to always pull before file edits and push after completed changes.
- 2026-04-18: Tightened post-edit language to explicit order: always commit first, then push.
- 2026-04-18: Updated `.vscode/settings.json` terminal auto-approve command patterns from the other-device path to this device path (`/Users/macmini/Documents/projects/solo-leveling`).
- 2026-04-18: Installed `font-meslo-for-powerlevel10k` on macOS and set VS Code integrated terminal font family to `MesloLGS NF` fallback chain for proper Oh My Zsh/Powerlevel10k glyph rendering.
