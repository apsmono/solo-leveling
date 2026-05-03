# Conventions

This file consolidates every convention used in the solo-leveling repository: how we write code, how we document changes, how we branch and merge, and how we name things.

---

## Git Conventions

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature / task | `agent/<agent-name>/<task-slug>/<scope>` | `agent/claude/library-search-cache/stage9` |
| Lead review | `lead/<reviewer>/<task-slug>` | `lead/claude/integration-smoke-fix` |
| Program milestone | `program/<milestone>` | `program/stage9-completion` |

### Sync Rules

1. **Before edits:** `git fetch --all --prune && git status -sb`
2. **If behind:** `git pull --ff-only`
3. **After any pull or push:** re-read `AI_CONTEXT.md` and `docs/ai-knowledge/continuation-plan.md`
4. **Post-edit (required):** commit first, then `git push` so remote stays in sync
5. **Prefer PR-based merges to `main`**; do not push direct to `main` when a task can conflict with another active task

### Commit Style

- Use conventional commit prefixes: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Keep the subject line under 72 characters
- Explain the *why* in the body, not just the *what*

---

## Code Conventions (Python)

### Import Style

- Use absolute imports with the `src.` prefix
- No relative imports
- Group imports: stdlib → third-party → local

```python
from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import FastAPI

from src.core.router import route_command
```

### Module Structure

Every module should follow this order:

1. Docstring explaining purpose and env vars
2. `from __future__ import annotations`
3. Imports
4. Module-level constants
5. Private helpers (`_function`)
6. Public API
7. If executable: `if __name__ == "__main__":` guard

### Type Hints

- Use `from __future__ import annotations` to avoid quoting forward references
- Use `dict[str, Any]`, `list[str]`, `str | None` syntax (Python 3.10+)
- Annotate all public function signatures

### Naming

| Construct | Convention | Example |
|-----------|------------|---------|
| Modules / packages | lowercase with underscores | `router.py`, `gdrive` |
| Classes | PascalCase | `SearchCache` |
| Functions / methods | lowercase with underscores | `route_command` |
| Constants / module globals | UPPER_SNAKE_CASE | `INTENT_MAP`, `SCOPES` |
| Private helpers | leading underscore | `_detect_intent`, `_service` |
| Type variables | PascalCase | `ReminderDict` (if used) |

### Error Handling

- Integration handlers catch `EnvironmentError` separately to show configuration issues
- Unexpected exceptions are logged with `logger.exception()` and returned as generic user-facing messages
- Never leak stack traces to API responses

### Logging

- Use `logging.getLogger(__name__)` in every module
- Log at `INFO` for successful operations, `WARNING` for recoverable issues, `ERROR` for failures
- Include context (query, ID, count) in log messages

---

## Documentation Conventions

### When to Update Docs

Update documentation in the same change whenever you alter:
- Behavior or workflow
- Structure or file locations
- Environment variables or dependencies
- Intent maps or command syntax

### File Location Rules

| Content Type | Location |
|-------------|----------|
| Architecture / system design | `docs/architecture/` |
| Formal decisions | `docs/decisions/NNN-slug.md` |
| AI cross-session memory | `docs/ai-knowledge/` |
| Durable research | `docs/research/YYYY-MM-DD.md` |
| Reusable templates | `docs/templates/` |
| Filled task cards | `docs/task-cards/` |
| Filled scorecards | `docs/scorecards/` |
| Personal development strategy | `docs/` root |

### Timestamp Format

- Use local device time: `YYYY-MM-DD HH-mm-ss`
- Command to generate: `date "+%Y-%m-%d %H-%M-%S"`

---

## Changelog Rules

- File: `CHANGELOG.md`
- Human-readable and curated; do not copy commit history verbatim
- Add entries in **reverse chronological order** (newest first inside each section)
- Grouped sections: `Added`, `Changed`, `Fixed`, `Removed`, `Docs`, `Decisions`
- Each entry states what changed and why it matters to a human reader

---

## Testing Conventions

### Framework

- Use `unittest` from the standard library
- Mock integration calls at the router level using `@patch("src.core.router.notion.search")`
- Isolate environment variables with `@patch.dict(os.environ, {...}, clear=True)`

### Test Organization

- `tests/test_integration_smoke.py` — router smoke tests and integration guardrails
- `tests/test_stage9_libraries.py` — library system tests with temp directories
- Live integration tests are gated behind `ENABLE_LIVE_SMOKE_TESTS=1`

### Running Tests

```bash
# All tests
python -m unittest tests.test_stage9_libraries tests.test_integration_smoke -v

# Single module
python -m unittest tests.test_stage9_libraries -v
```

---

## AI Collaboration Rules

1. **Read before starting:** `README.md`, `AGENTS.md`, `AI_CONTEXT.md`, `docs/ai-working-notes.md`
2. **Read before architecture changes:** `docs/architecture/command-center.md`
3. **Prefer small, explicit edits** over broad speculative scaffolding
4. **Record assumptions and decisions** in documentation immediately
5. **Write after finishing:** update `docs/ai-working-notes.md`, `AI_CONTEXT.md` (if priorities changed), `CHANGELOG.md`, and create a decision record if a significant choice was made
