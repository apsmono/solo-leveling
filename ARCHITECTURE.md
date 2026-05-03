# Architecture

High-level system architecture for the solo-leveling command center.

For deep-dive architecture, see:
- `docs/architecture/command-center.md` — full layered diagram, data flow, and stage table
- `docs/architecture/integrations.md` — per-service contracts and security rules

---

## Layers

```
┌─────────────────────────────────────────┐
│  Command Interface                      │  HTTP POST /command {"text": "..."}
│  (FastAPI)                              │  GET /healthz
├─────────────────────────────────────────┤
│  Brain Core                             │
│  • Intent Detection (keyword map)       │
│  • Command Dispatch                     │
│  • Workflow Composition                 │
│  • Notification Scheduler               │
│  • Personal Library (Stage 9)           │
├─────────────────────────────────────────┤
│  Integration Layer                      │
│  • Notion API                           │
│  • Google Drive API                     │
│  • Gmail API                            │
├─────────────────────────────────────────┤
│  AI Agent Layer                         │
│  • Gemini API (httpx)                   │
└─────────────────────────────────────────┘
```

---

## Data Flows

### 1. Inbound Command

```
HTTP POST /command
    │
    ▼
src/app.py  →  route_command(text)
    │
    ▼
src/core/router.py  →  _detect_intent(text)
    │
    ├──► keyword match  →  _dispatch(intent, text)  →  handler()
    │
    └──► compound workflow  →  handle_workflow_command()
```

### 2. Library Deep Capture

```
"add to library: <topic>"
    │
    ▼
src/core/libraries.py  →  _handle_library_capture()
    │
    ├──► sensitive content check
    ├──► search existing entries
    ├──► call Gemini for analysis  →  JSON with category, summary, facts, Q&A
    ├──► create research bundle (7 markdown files)
    ├──► auto-create term + reference + thought entries
    └──► rebuild library/index.json  +  invalidate search cache
```

### 3. Workflow Execution

```
"summarise my inbox and save to notion"
    │
    ▼
src/core/workflows.py  →  _workflow_inbox_summary_to_notion()
    │
    ├──► gmail.inbox_summary(limit=5)
    └──► notion.create_page(parent_id, title, content)
```

---

## Key Modules

| Module | File | Responsibility |
|--------|------|---------------|
| FastAPI App | `src/app.py` | HTTP server, lifespan, health endpoint |
| Router | `src/core/router.py` | Intent detection, dispatch, all command handlers |
| Workflows | `src/core/workflows.py` | Multi-step integration chains |
| Scheduler | `src/core/scheduler.py` | APScheduler jobs, reminders, digests |
| Libraries | `src/core/libraries.py` | File-based knowledge capture, search, indexing |
| Config | `src/core/config.py` | Environment variable loader |
| AI Dispatcher | `src/agents/dispatcher.py` | Gemini API wrapper |
| Notion Client | `src/integrations/notion/client.py` | Search, read, create pages |
| Drive Client | `src/integrations/gdrive/client.py` | List, read, create docs |
| Gmail Client | `src/integrations/gmail/client.py` | List unread, search, inbox summary |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Web framework | FastAPI + Uvicorn |
| HTTP client | httpx |
| Scheduling | APScheduler |
| AI provider | Gemini API (REST via httpx) |
| Notion SDK | notion-client |
| Google APIs | google-api-python-client, google-auth-oauthlib |
| Environment | python-dotenv |
| Container | Python 3.13-slim, non-root user |

---

## State and Persistence

| Data | Location | Persistence |
|------|----------|-------------|
| Knowledge entries | `library/` markdown files | Git + Docker volume |
| Library index | `library/index.json` | Regenerated on write |
| Reminders | `data/reminders.json` | Docker volume |
| Gmail token | `.gmail_token.json` | File (gitignored) |

---

## Extensibility

Adding a new command:

1. Add intent keywords to `INTENT_MAP` in `src/core/router.py`
2. Add handler function in `src/core/router.py`
3. Wire handler into `_dispatch()`
4. Add smoke test in `tests/test_integration_smoke.py`
5. Update `README.md` help text if user-facing

Adding a new integration:

1. Create `src/integrations/<service>/client.py`
2. Add env var loading to `src/core/config.py`
3. Add health check to `_handle_health()` in `src/core/router.py`
4. Document in `docs/architecture/integrations.md`
5. Add smoke tests and optional live tests
