# Documentation Map

This folder contains the full planning structure for the project, including system architecture and decision records.

## Architecture

- `architecture/command-center.md` — full brain and command-center architecture, data flow, and implementation stages.
- `architecture/integrations.md` — integration map and contracts for WhatsApp, Notion, Google Drive, Gmail, and notifications.

## Source Code

- `../src/README.md` — code folder structure and setup rules.
- `../src/integrations/whatsapp/` — webhook handler and API client (Meta + Twilio).
- `../src/core/router.py` — command intent parser and dispatcher.
- `../src/core/config.py` — environment variable loader.
- `../requirements.txt` — Python dependencies.
- `../.env.example` — environment variable template (copy to `.env`, never commit).

## Decisions

- `decisions/001-command-center-scope.md` — decision to redefine the repo as the central brain and command center.
- `decision-log-template.md` — reusable template for future decision records.

## Planning Documents

- `self-development-system.md` — personal growth operating model.
- `financial-freedom-strategy.md` — wealth-building system and constraints.
- `habit-system.md` — recurring behaviors, scorekeeping, and adjustment rules.
- `review-rhythm.md` — review cadence and checkpoint questions.
- `AI_CHANGELOG_POLICY.md` — changelog format, timestamp standard, and maintenance rules.
- `SETUP_SECRETS.md` — step-by-step credentials and service setup checklist for local runtime.

## AI Knowledge Base

Split into focused files inside `docs/ai-knowledge/`. Entry point: `docs/ai-working-notes.md`.

| File                                                                           | Contents                                                |
| ------------------------------------------------------------------------------ | ------------------------------------------------------- |
| [`ai-knowledge/build-history.md`](ai-knowledge/build-history.md)               | Repo build history and stage completion status          |
| [`ai-knowledge/conventions.md`](ai-knowledge/conventions.md)                   | Changelog rules, doc update obligations, file structure |
| [`ai-knowledge/error-log.md`](ai-knowledge/error-log.md)                       | Error log with root cause, fix, and prevention rules    |
| [`ai-knowledge/integration-patterns.md`](ai-knowledge/integration-patterns.md) | Per-service integration gotchas and working patterns    |
| [`ai-knowledge/security-rules.md`](ai-knowledge/security-rules.md)             | Non-negotiable security constraints                     |
| [`ai-knowledge/continuation-plan.md`](ai-knowledge/continuation-plan.md)       | What is done, what is next, env var reference           |

## Usage Rules

- When architecture or integration scope changes, update the relevant `architecture/` doc.
- When making a major decision, create a new numbered record in `decisions/` using `decision-log-template.md`.
- Update the relevant planning document when a strategy, workflow, or definition changes.
- Reflect meaningful documentation updates in `CHANGELOG.md`.

## Recommended Flow

1. For system changes: update `architecture/command-center.md` or `architecture/integrations.md`.
2. For major decisions: create a new file in `decisions/` from the template.
3. For strategy or habit changes: update the relevant planning doc.
4. Always: update `CHANGELOG.md` with the meaningful outcome.
