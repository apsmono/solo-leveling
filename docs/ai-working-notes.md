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

- **2026-04-22: Added owner self-review and ready-to-use operating templates.** Updated `docs/ai-employer-operating-system.md` to include Main Brain self-performance evaluation and self-management metric in weekly scoring. Added `docs/templates/task-card-template.md` and `docs/templates/weekly-rl-okr-scorecard-template.md` so AI teams can execute policy immediately with no manual formatting.
- **2026-04-22: AI employer governance + OKR responsibility system adopted.** Added `docs/ai-employer-operating-system.md` as the canonical policy for role-branch-authority control, unified task schema, RL1-RL5 responsibility model, OKR scoring formulas, responsibility-level testing thresholds, and revenue-impact assignment rules. Refactored `docs/ai-team-coordination.md` into operational guidance aligned to the new governance model, and added formal decision record `docs/decisions/003-ai-employer-governance-model.md`.
- **2026-04-22: Session recap + no-WhatsApp execution plan added.** Added `docs/SESSION-RECAP-2026-04-22.md` to preserve this session's guidance (latest WhatsApp setup direction, legal-verification decision framework, and API-setup UI troubleshooting), and added `docs/PLAN-WITHOUT-WHATSAPP-2026-04-22.md` with a phased plan to continue Stage 9 progress while WhatsApp integration is paused.
- **2026-04-21: MULTI-AI-003 CI pipeline implemented.** Created `.github/workflows/ci.yml` — GitHub Actions pipeline that runs all 23 tests on every push/PR to `main`. Credential-gated live tests auto-skip (no secrets needed in CI). YAML validated locally. Task doc at `docs/TASK-MULTI-AI-003.md`.
- **2026-04-21: MULTI-AI-002 completed and validated.** Implemented `tests/test_integration_smoke.py` for credential-aware integration smoke coverage (Notion, Drive, Gmail, router flows, WhatsApp payload parsing, AI dispatch/workflow guardrails), hardened Gmail live-smoke to avoid unintended interactive OAuth in headless environments, added exact smoke-test run commands in docs, and validated with `23 tests, 3 skipped` using `python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v`.
- **2026-04-21: Monitor AI staged the next coordinated task.** Updated `AI_CONTEXT.md`, `docs/ai-team-coordination.md`, and `docs/ai-knowledge/continuation-plan.md` so MULTI-AI-001 is treated as completed and the next coordinated task is MULTI-AI-002 (`docs/TASK-MULTI-AI-002.md`) for credential-aware integration smoke coverage.
- **2026-04-21: Monitor AI normalized MULTI-AI docs state.** Updated `docs/TASK-MULTI-AI-001.md` from READY_FOR_ASSIGNMENT to DONE, checked acceptance criteria to match merged reality, and removed stale "pending changelog" note from `docs/TASK-MULTI-AI-001-validation.md`. This resolves documentation drift and keeps multi-AI status auditable.
- **2026-04-21: Cross-device continuity helper added.** Added `scripts/device-sync.sh` with three modes: `switch-out` (pre-leave checklist), `switch-in` (fetch/pull/status + required read order), and `bootstrap-prompt` (ready-to-paste startup prompt). Added prompt file at `prompts/cross-device-startup.prompt.txt`. This is the standard way to keep AI context consistent across devices.
- **2026-04-21: TASK-MULTI-AI-001 (Library Search Optimization) COMPLETED.** Executed first full multi-AI coordinated task. Research AI profiled bottleneck (200ms per search due to \_build_library_index() on every call), Monitor AI designed in-memory LRU cache strategy, Executor AI implemented SearchCache class with TTL + integration, Quality AI validated 100% improvement (1.9ms → 0ms warm), Monitor AI merged to main. All 9 tests pass (3 new cache tests). Proves async handoff model works: Research → Design → Implement → Validate → Merge across 4 feature branches. Feature committed: commit merged to main (ff7d2069). Task took ~70 min wall-clock. See `docs/TASK-MULTI-AI-001*.md` files for research, design, validation details.
- **2026-04-21: Multi-AI team coordination framework established.** Added `docs/ai-team-coordination.md` (comprehensive team structure, roles, task tracking, communication protocol) and `docs/TASK-MULTI-AI-001.md` (first pilot task: Library Search Optimization with detailed execution flow). Defined Monitor AI (me) as coordinator, established git-based async workflow, and ready to execute first multi-AI task proof-of-concept. See `docs/ai-team-coordination.md` for team roles, git discipline, and escalation paths.
- **2026-04-21: Researched AI teamwork patterns and captured to library.** Created comprehensive research bundle covering 5 core roles (Strategic Planner, Executor, Coordinator, Reviewer, Domain Expert), task allocation patterns, async handoff protocols, PM AI responsibilities, and scaling from 1 to 10+ AIs. Auto-generated term definition, reference guide, and thought entries. Commit fc62835.
- 2026-04-20: Added a deployment baseline with `Dockerfile` and `.dockerignore`. The container runs the FastAPI WhatsApp webhook and assumes mounted persistence for `library/` and `data/` so Stage 9 writes and reminders survive container restarts.
- 2026-04-20: Added weekly Stage 9 maintenance support. `library maintenance` now returns a cleanup checklist plus live coverage counts, `library maintenance schedule` reports the configured reminder slot, and the scheduler can send a recurring weekly WhatsApp maintenance reminder through new env vars.
- 2026-04-20: Cleaned active Stage 9 doc entry points so `docs/README.md` and `docs/personal-library-implementation-checklist.md` now describe the local `library/` workflow first. Older Notion schema material is retained there only as historical reference.
- 2026-04-20: Added executable Stage 9 regression coverage in `tests/test_stage9_libraries.py`. The tests verify validation failures, local entry creation, deep bundle capture, and indexed retrieval commands using a temporary local library root.
- 2026-04-20: Added indexed retrieval for Stage 9 local library. `library/index.json` is now generated from filesystem contents, and new commands can search the library, locate research bundles, and summarize bundle overviews.
- 2026-04-20: Added deep Stage 9 intake workflow for `add to library` / `add to my personal knowledge`. The command now categorizes the topic, searches existing library entries, identifies valuable information to track, and writes a full research bundle with raw input, search history, research notes, Q/A log, logic trail, and conclusion.
- 2026-04-20: Terminology pivot applied — in this repo, "library" now means local folder `library/` only. Stage 9 handlers were switched from Notion-backed capture/search to local markdown storage under `library/profile`, `library/terms`, `library/books`, `library/articles`, `library/thoughts`, and `library/references`.
- 2026-04-18: Implemented first Stage 9 code slice: created `src/core/libraries.py` and wired new router intents (`library_profile`, `library_term`, `library_book`, `library_article`, `library_thought`, `library_review`) so knowledge profile and library capture commands are now routable.
- 2026-04-18: Historical note (superseded on 2026-04-20): Stage 9 runtime initially used Notion page capture mode under `NOTION_WORKFLOW_PARENT_ID`.
- 2026-04-18: Started implementation of multi-agent coordination model: standardized `agent/<agent-name>/<task-slug>/<stage-or-scope>` branches, PR-first merge guidance for overlapping work, task-claim ownership, and handoff checklist expectations.
- 2026-04-18: Expanded Stage 9 library design with MCP-aligned knowledge profile scope (skills, interests, domains, learning priorities, focus themes) and explicit sensitive-data exclusions.
- 2026-04-18: Added a standard git preflight rule before preparation/setup (`git fetch --all --prune && git status -sb`) in setup and conventions docs.
- 2026-04-18: Added a mandatory AI sync rule in `.github/copilot-instructions.md` and `AGENTS.md` to always pull before file edits and push after completed changes.
- 2026-04-18: Tightened post-edit language to explicit order: always commit first, then push.
- 2026-04-18: Updated `.vscode/settings.json` terminal auto-approve command patterns from the other-device path to this device path (`/Users/macmini/Documents/projects/solo-leveling`).
- 2026-04-18: Installed `font-meslo-for-powerlevel10k` on macOS and set VS Code integrated terminal font family to `MesloLGS NF` fallback chain for proper Oh My Zsh/Powerlevel10k glyph rendering.
