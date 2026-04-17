# Conventions

Standards established in this repository that all contributors (human and AI) must follow.

## Changelog

- File: `CHANGELOG.md` at repo root.
- Timestamp format: `YYYY-MM-DD HH-mm-ss` (local device time, not UTC).
- To get the current timestamp in terminal: `date "+%Y-%m-%d %H-%M-%S"`
- New entries go at the top of the relevant subsection (newest first).
- Sections used: `Added`, `Changed`, `Fixed`, `Removed`, `Docs`, `Decisions`.
- Never paste raw git log output — write impact, not implementation noise.
- Full policy: `docs/AI_CHANGELOG_POLICY.md`.

## Documentation Updates

Every meaningful change must update the nearest source-of-truth file in the same change:

- `AI_CONTEXT.md` → when scope, phase, or active document list changes
- `AGENTS.md` → when agent rules or the operating model changes
- `docs/README.md` → when new files or folders are added to `docs/`
- `docs/architecture/integrations.md` → when any integration scope or status changes
- `docs/ai-knowledge/continuation-plan.md` → when stages are completed or new work begins

## Decision Records

- Location: `docs/decisions/NNN-slug.md` (sequentially numbered).
- Template: `docs/decision-log-template.md`.
- Required fields: Date (`YYYY-MM-DD HH-mm-ss`), Status, Context, Decision, Why, Alternatives, Consequences, Related Updates.
- Create a record any time: scope changes, integration approach is chosen, security policy is set, or a direction is permanently changed.

## File Structure Rules

| Path                          | Purpose                                                      |
| ----------------------------- | ------------------------------------------------------------ |
| `docs/`                       | All documentation, planning, architecture, decisions         |
| `docs/architecture/`          | System design, data flows, integration specs                 |
| `docs/decisions/`             | Formal decision log (numbered files)                         |
| `docs/ai-knowledge/`          | AI cross-session memory (this folder)                        |
| `data/`                       | Runtime-generated local state such as persisted reminders    |
| `src/`                        | All Python source code                                       |
| `src/integrations/<service>/` | One subfolder per external service; each needs a `README.md` |
| `src/core/`                   | Router, config loader, shared utilities                      |
| `src/agents/`                 | AI agent wrappers                                            |
| `prompts/`                    | Reusable AI prompt files                                     |
| `tests/`                      | Add when executable logic needs validation (not yet created) |
