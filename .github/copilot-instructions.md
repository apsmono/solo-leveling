# Copilot Instructions

## Repository Focus

This repository is for building structured self-development and financial freedom systems. Treat clarity, maintainability, and decision traceability as primary goals.

## Before Making Changes

- Read `README.md` and `AI_CONTEXT.md` first.
- Respect the documentation-first nature of the project.
- Prefer minimal, targeted changes that improve the repository's usefulness.

## Working Rules

- Keep AI-facing documentation current whenever repository structure or workflows change.
- Update related descriptions and documentation whenever a change modifies behavior, purpose, usage, or structure.
- Update `CHANGELOG.md` for every notable change using local device time in the format `YYYY-MM-DD HH-mm-ss`.
- Git sync is mandatory on each change cycle:
  - Before editing files: run `git fetch --all --prune && git status -sb`; if behind, run `git pull --ff-only`.
  - Post-sync (after any `git pull` or `git push`): re-read `AI_CONTEXT.md` and `docs/ai-knowledge/continuation-plan.md` to update your understanding of the current phase, completed stages, and active priorities.
  - Post-edit (required): always commit first, then run `git push` so local and remote stay aligned.
- For concurrent AI work, use Git task isolation:
  - Work on `agent/<agent-name>/<task-slug>/<stage-or-scope>` branches.
  - Use pull requests to merge into `main` when a task overlaps with active work.
  - Claim task ownership before editing and include a short handoff summary before finishing.
- When proposing new folders or files, align them to an actual use case.
- Avoid generic filler content and unsupported assumptions.
- If code is added, document how to run, verify, and maintain it.

## Approval Gate For Policy Updates

- If a request includes policy/governance/process changes, pause normal execution and present suggestions first.
- For each suggestion, state what will change and why it is needed.
- Apply policy/governance changes only after explicit owner approval.
- Record accepted policy/governance decisions in `docs/decisions/` and `CHANGELOG.md`.

## Research Recording Rule

- All substantial research outputs must be saved as durable documents under `docs/research/`.
- Research-only sessions still require documentation updates when notable outputs are produced.

## Changelog Standard

- Keep changelog entries readable by humans first.
- Do not dump raw commit logs into `CHANGELOG.md`.
- Group entries under clear headings such as `Added`, `Changed`, `Fixed`, `Removed`, `Docs`, and `Decisions`.
- Make each entry concise, specific, and traceable to the user-visible or project-visible impact.

## Preferred Deliverables

- Clear plans
- Reusable templates
- Explicit instructions
- Concise rationale for structural decisions
