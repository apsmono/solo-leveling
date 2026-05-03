# AGENTS.md

## Purpose

This repository is the central brain and command center for the owner's personal operating system. It holds persistent context, routes commands from WhatsApp, integrates with Notion, Google Drive, and Gmail, and orchestrates AI agents for complex tasks.

## Current State

- Stages 1–8 are implemented, including multi-step workflow chains and the proactive notification scheduler.
- Stage 9 (Personal Knowledge Libraries) is the main active stage.
- The owner switches devices frequently and collaborates with multiple AI tools. Session knowledge must be written back to the repo after every working session.
- AI assistants should treat documentation accuracy and decision traceability as first-class work.
- Full build history, error log, integration patterns, and continuation plan: `docs/ai-working-notes.md`.

## Agent Rules

- Read `README.md`, `AI_CONTEXT.md`, `AGENTS.md`, and `docs/ai-working-notes.md` before making any substantial changes.
- Read `docs/architecture/command-center.md` before adding any integration code or command routing logic.
- Prefer small, explicit edits over broad speculative scaffolding.
- Record important assumptions, operating rules, and project decisions in documentation.
- Update documentation and file descriptions whenever a change affects behavior, structure, workflow, or meaning.
- Update `CHANGELOG.md` for every notable change using local device time in the format `YYYY-MM-DD HH-mm-ss`. Get the timestamp with: `date "+%Y-%m-%d %H-%M-%S"`
- Keep repository sync strict for every file-change session:
  - Before edits: run `git fetch --all --prune && git status -sb`; if behind, run `git pull --ff-only`.
  - Post-sync (after any `git pull` or `git push`): re-read `AI_CONTEXT.md` and `docs/ai-knowledge/continuation-plan.md` to refresh your understanding of current phase, completed stages, and active priorities.
  - Post-edit (required): always commit first, then run `git push` so remote stays in sync.
- Multi-agent Git coordination is mandatory for concurrent work:
  - Use a feature branch per task: `agent/<agent-name>/<task-slug>/<stage-or-scope>`.
  - Prefer PR-based merges to `main`; do not push direct to `main` when a task can conflict with another active task.
  - Claim ownership of a task before editing and keep one active owner per task at a time.
  - Include a handoff summary in the same change: what was done, what is pending, and what the next agent should do.
- **Worktree isolation for parallel agents:**
  - If another agent is already working in this checkout, start a new worktree with `claude --worktree <name>` instead of editing the same files.
  - For subagents that may edit code in parallel, set `isolation: worktree` in the subagent frontmatter so each gets its own temporary branch and directory.
  - Clean up worktrees when done: `git worktree remove <path>` or let Claude prompt you on exit.
  - See `CLAUDE.md` → "Parallel Work with Git Worktrees" for full details.
- When adding integration code, update `docs/architecture/integrations.md` to reflect the current state.
- When making a significant scope, structure, or policy decision, create a numbered record in `docs/decisions/`.
- Never store credentials, API keys, or secrets in this repository.
- Do not invent business claims, metrics, or roadmap items that are not documented in the repository.

## Approval Gate And Research Recording Protocol

- For policy/governance/process updates, pause normal execution and propose updates first.
- For each proposed update, include the specific change and the reason it is needed.
- Continue policy-governance execution only after explicit owner approval.
- Record all substantial research outputs in `docs/research/` as durable files.
- Record each accepted policy/governance decision in `docs/decisions/` and `CHANGELOG.md`.
- If approval is not explicit, remain in proposal mode and do not apply policy changes.

## Persistent Memory Rule (IMPORTANT)

The owner works across multiple devices and collaborates with multiple AI tools. Context is never guaranteed to carry over. Every AI agent that does meaningful work in this repo **must write its session knowledge back before finishing**:

**Absolute rule for every session:**

- **ALWAYS read before starting.**
- **ALWAYS write after finishing.**

1. **Update `docs/ai-working-notes.md`** with any new patterns, errors, fixes, or decisions discovered during the session. Add to the relevant section; do not overwrite — only append or update.
2. **Update `AI_CONTEXT.md`** if the current phase, completed stages, or active priorities have changed.
3. **Update `CHANGELOG.md`** with all notable changes made during the session.
4. **Create a `docs/decisions/NNN-*.md`** if any significant architectural or policy choice was made.

Think of it this way: when you finish, the next AI that opens this repo should be able to read the docs and know exactly what you did, what you found, and where to continue — without needing to re-explore the codebase.

## Changelog Rule

- Keep `CHANGELOG.md` human-readable and curated rather than copying commit history.
- Add new entries in reverse chronological order, with newest first inside each active section.
- Use grouped sections such as `Added`, `Changed`, `Fixed`, `Removed`, `Docs`, and `Decisions` when relevant.
- Each entry should state what changed and why it matters to a human reader.

## Expected Output Style

- Keep plans actionable and concrete.
- Separate confirmed facts from proposed next steps.
- When creating frameworks or templates, optimize for maintainability and reuse.
