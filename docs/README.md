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

## Testing

- Stage 9 local regression suite:
  - `/Users/macmini/Documents/projects/solo-leveling/.venv/bin/python -m unittest tests.test_stage9_libraries -v`
- Integration smoke suite (credential-aware):
  - `/Users/macmini/Documents/projects/solo-leveling/.venv/bin/python -m unittest tests.test_integration_smoke -v`
- Router-only smoke tests (no credentials):
  - `/Users/macmini/Documents/projects/solo-leveling/.venv/bin/python -m unittest tests.test_integration_smoke.RouterSmokeTests -v`

Smoke suite behavior:

- Router smoke tests are mock-based and should pass without secrets.
- Live integration smoke tests will skip with explicit messages when credentials are unavailable.
- Gmail live smoke requires `GMAIL_TOKEN_PATH` or an OAuth credential file and is non-interactive by default unless `ALLOW_INTERACTIVE_OAUTH_SMOKE=true` is set.

## Local Environment Templates

- `../config/zsh/.zshrc.example` — sanitized zsh profile template (Oh My Zsh, powerlevel10k, plugins, nvm).
- `../config/zsh/.zprofile.example` — sanitized login-shell profile template (Homebrew shellenv + local PATH).
- `../.vscode/settings.json` — workspace terminal defaults (zsh login shell, MesloLGS NF font, iTerm external terminal).

## Decisions

- `decisions/001-command-center-scope.md` — decision to redefine the repo as the central brain and command center.
- `decisions/003-ai-employer-governance-model.md` — decision to adopt role-branch-authority governance with OKR-based responsibility valuation.
- `decision-log-template.md` — reusable template for future decision records.

## Planning Documents

- `personal-knowledge-system-design.md` — research on self-development strategies, Stage 9 library structure, integration plan, and implementation roadmap. Parts of this file are historical and should be read together with the local-library rules in `AI_CONTEXT.md`.
- `personal-library-implementation-checklist.md` — step-by-step guide for the current local `library/` workflow, command testing, indexing/retrieval, and Stage 9 enhancement roadmap. Historical Notion schema notes are retained there only as reference.
- `self-development-system.md` — personal growth operating model.
- `financial-freedom-strategy.md` — wealth-building system and constraints.
- `habit-system.md` — recurring behaviors, scorekeeping, and adjustment rules.
- `review-rhythm.md` — review cadence and checkpoint questions.
- `AI_CHANGELOG_POLICY.md` — changelog format, timestamp standard, and maintenance rules.
- `SETUP_SECRETS.md` — step-by-step credentials and service setup checklist for local runtime.

## Ready-to-Use Templates

- `templates/task-card-template.md` — structured task definition template with objective/KR linkage, RL assignment, validation gate, and handoff section.
- `templates/weekly-rl-okr-scorecard-template.md` — weekly scoring template for KR progress, AI RL evaluation, owner self-review, and assignment-policy updates.
- `templates/weekly-rl-okr-scorecard-example-2026-W17.md` — prefilled example scorecard using current documented team/project state for immediate weekly scoring kickoff.
- `ai-team-coordination.md` — operational coordination flow for multi-AI execution lifecycle, branch flow, and escalation.
- `ai-employer-operating-system.md` — canonical employer governance model (OKR system, responsibility-level testing, scoring, assignment policy).

## Operational Records (Filled, Non-Template)

- `task-cards/` — completed task cards for real execution work (copy from template, then fill).
- `scorecards/` — weekly RL/OKR scorecards and owner self-evaluation records.
- `task-cards/MULTI-AI-004-weekly-performance-kickoff-2026-04-22.md` — first filled task-card example.
- `scorecards/weekly-rl-okr-scorecard-2026-W17-main-brain.md` — first filled owner scorecard record.

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
