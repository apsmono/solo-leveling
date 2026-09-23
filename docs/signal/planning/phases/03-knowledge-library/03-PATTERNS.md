# Phase 3: Knowledge Library + Conceptual Search + AI Guide - Pattern Map

**Mapped:** 2026-05-30
**Files analyzed:** 12 new/modified files
**Analogs found:** 11 / 12

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/vector/search.py` | service | CRUD + request-response (embed + DB query) | `src/vector/cache.py` — cosine distance query, parameterized SQL, owner_id scoping | exact |
| `src/core/intent_parser.py` | service | request-response (LLM call) | `src/agents/dispatcher.py` — `run_agent()` wrapper with system prompt | exact |
| `src/api/guide.py` | route | request-response | `src/api/library.py` — `APIRouter`, `Depends(require_auth)`, `HTTPException` | exact |
| `src/core/router.py` (modify) | router / dispatcher | EVOLVE — replace `_detect_intent` | `src/core/router.py` itself — `_detect_intent()` + `_dispatch()` | self-analog |
| `src/api/library.py` (modify) | route | EVOLVE — add `/search`, `/recent` | `src/api/library.py` itself — existing `list_entries`, `get_entry` patterns | self-analog |
| `src/api/v1_router.py` (modify) | config / wiring | EVOLVE — register guide router | `src/api/v1_router.py` itself — `router.include_router()` pattern | self-analog |
| `tests/test_vector_search.py` | test | unit + integration | `tests/test_vector_foundation.py` — mock pool, mock embed, async test pattern | exact |
| `tests/test_intent_parser.py` | test | unit | `tests/test_vector_foundation.py` — mock pattern, env isolation | exact |
| `tests/test_guide_api.py` | test | unit + integration | `tests/test_library_api.py` — `TestClient`, mock auth | exact |
| `dashboard/src/components/guide/AIGuidePanel.tsx` | UI component | render | `dashboard/src/components/library/EntryAIPanel.tsx` — panel with chat thread, input, state | role-match |
| `dashboard/src/components/guide/CommandBar.tsx` | UI component | render + event | `dashboard/src/components/dashboard/CommandInput.tsx` — text input with submit | role-match |
| `dashboard/src/components/guide/StatusBanner.tsx` | UI component | render (read-only) | `dashboard/src/components/dashboard/Overview.tsx` — stats cards, metrics display | role-match |
| `dashboard/src/components/guide/DistractionGate.tsx` | UI component | render + modal | `dashboard/src/components/library/LinkCaptureModal.tsx` — modal with form, save action | role-match |
| `dashboard/src/components/dashboard/DashboardPage.tsx` (modify) | layout | EVOLVE — integrate Guide panel | `dashboard/src/components/dashboard/DashboardPage.tsx` itself — tab switcher, lazy imports | self-analog |
| `dashboard/src/lib/api.ts` (modify) | client | EVOLVE — add guide endpoints | `dashboard/src/lib/api.ts` itself — `apiGet`, `apiPost`, `sendCommand` patterns | self-analog |
| `dashboard/src/hooks/useApi.ts` (modify) | hooks | EVOLVE — add guide hooks | `dashboard/src/hooks/useApi.ts` itself — `useState` + `useCallback` + `useEffect` pattern | self-analog |

---

## Pattern Assignments

### `src/vector/search.py` (service, async CRUD + embedding)

**Analog:** `src/vector/cache.py` — this is the closest pattern: parameterized SQL with `%s` placeholders, `get_pool().connection()` async context manager, `owner_id` scoping, embedding via `embed_text()`.

**Imports pattern** (mirror `cache.py` lines 1-10):
```python
from __future__ import annotations

import logging
from typing import Any, Literal

from src.vector.db import get_pool
from src.vector.embed import embed_text

logger = logging.getLogger(__name__)
```

**Parameterized SQL pattern** (mirror `cache.py` lines 32-42):
```python
async with get_pool().connection() as conn:
    rows = await conn.fetchall(
        """
        SELECT entry_id, section, source_url, 1 - (embedding <=> %s::vector) AS similarity
        FROM signal_embeddings
        WHERE owner_id = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (vec, owner_id, vec, limit),
    )
```

**Hybrid search pattern** (from RESEARCH.md Pattern 1):
```python
async def search_library(
    query: str,
    owner_id: str,
    mode: Literal["keyword", "vector", "hybrid"] = "hybrid",
    limit: int = 12,
) -> list[dict[str, Any]]:
    if mode in ("keyword", "hybrid"):
        keyword_results = _get_store().search_entries(query, limit=limit)
        if mode == "keyword":
            return keyword_results
        if len(keyword_results) >= limit // 2:
            return keyword_results
    # Vector search path...
```

**Owner-scoping pattern** (from `cache.py`):
- Every DB query includes `WHERE owner_id = %s`
- `owner_id` is a required parameter (no default)

---

### `src/core/intent_parser.py` (service, LLM call)

**Analog:** `src/agents/dispatcher.py` — `run_agent(task, context, system)` is the exact function to call.

**Imports pattern**:
```python
from __future__ import annotations

import json
import logging
from typing import Any

from src.agents.dispatcher import run_agent

logger = logging.getLogger(__name__)
```

**Structured output pattern** (from RESEARCH.md Pattern 2):
```python
_INTENT_SYSTEM_PROMPT = """You are an intent parser for a personal knowledge system.
Given a user's natural language command, classify it into one of these intents and extract parameters.

Intents: library_search, library_capture, library_qa, status, help, park_distraction, unknown

Respond with valid JSON only:
{
  "intent": "library_search",
  "params": {"query": "machine learning papers"},
  "confidence": 0.95
}"""

async def parse_intent(text: str) -> dict[str, Any]:
    try:
        response = run_agent(
            task=f"Parse this command: {text}",
            system=_INTENT_SYSTEM_PROMPT,
        )
        parsed = json.loads(response)
        return {
            "intent": parsed.get("intent", "unknown"),
            "params": parsed.get("params", {}),
            "confidence": parsed.get("confidence", 0.5),
        }
    except Exception:
        # Fallback to keyword map
        from src.core.router import _detect_intent
        intent = _detect_intent(text)
        return {"intent": intent, "params": {"text": text}, "confidence": 0.3}
```

**Fallback pattern** (from `cache.py` best-effort):
- Try/except around the entire body
- On any exception, fall back to keyword `_detect_intent`
- Never crash the command flow

---

### `src/api/guide.py` (route, request-response)

**Analog:** `src/api/library.py` — exact pattern for all new route files.

**Imports pattern** (mirror `library.py` lines 1-17):
```python
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import require_auth

router = APIRouter()
```

**Auth dependency pattern** (from `library.py` line 135):
```python
async def guide_command(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    owner_id = user.get("email", user.get("uid", "default-owner"))
    # ... handler logic
```

**Return shape pattern** (from `library.py` lines 169-174):
```python
return {
    "entries": entries,
    "total": len(entries),
    "mode": mode,
    "query": query,
}
```

---

### `src/core/router.py` — EVOLVE (replace `_detect_intent`)

**Analog:** `src/core/router.py` itself — modify existing `route_command` to call `parse_intent`.

**Evolution pattern**:
```python
async def route_command(text: str, source: str = "api") -> str:
    from src.core.intent_parser import parse_intent
    parsed = await parse_intent(text)
    intent = parsed["intent"]
    params = parsed.get("params", {})
    logger.info("Intent detected: %s (confidence=%.2f)", intent, parsed.get("confidence", 0))
    reply = await _dispatch_async(intent, text, params)
    _log_command(text, intent, reply, source)
    return reply
```

**Key constraint:** `route_command` is currently synchronous. The EVOLVE must either:
1. Make `route_command` async (breaking change for `/command` endpoint and Telegram webhook), OR
2. Keep `route_command` sync but fire `parse_intent` via `asyncio.run()` (blocks event loop), OR
3. Add a new `route_command_async` for API use while keeping `route_command` sync for Telegram

**Decision:** Option 3 — add `route_command_async` for the Guide API and `/command` endpoint; keep `route_command` sync for Telegram webhook compatibility. The `/command` endpoint in `app.py` is already async, so it can call `route_command_async`.

---

### `src/api/library.py` — EVOLVE (add `/search`, `/recent`)

**Analog:** `src/api/library.py` itself — existing `list_entries`, `get_entry` patterns.

**New endpoint pattern** (from RESEARCH.md):
```python
@router.post("/library/search")
async def search_library(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    query = str(payload.get("query", "")).strip()
    mode = str(payload.get("mode", "hybrid")).lower()
    limit = min(int(payload.get("limit", 12)), 50)
    if not query:
        raise HTTPException(status_code=400, detail="Missing 'query' in request body.")
    owner_id = user.get("email", user.get("uid", "default-owner"))
    # ... call vector search
```

---

### `dashboard/src/components/guide/AIGuidePanel.tsx` (UI component)

**Analog:** `dashboard/src/components/library/EntryAIPanel.tsx` — panel with chat thread, input area, loading state.

**Component pattern** (from RESEARCH.md Pattern 3):
```typescript
interface AIGuidePanelProps {
  activeView?: string;
}

export function AIGuidePanel({ activeView }: AIGuidePanelProps) {
  const { metrics } = useGuideStatus();
  const { messages, send, loading } = useGuideChat();
  const [distractionOpen, setDistractionOpen] = useState(false);

  return (
    <div className="flex flex-col h-full border-l border-border bg-surface">
      <StatusBanner metrics={metrics} />
      <ChatThread messages={messages} loading={loading} />
      <CommandBar onSend={send} onPark={() => setDistractionOpen(true)} />
      <DistractionGate open={distractionOpen} onClose={setDistractionOpen} />
    </div>
  );
}
```

**State lifting pattern** (from Pitfall 5 mitigation):
- AI Guide state must be lifted to `DashboardPage` level or use a React context provider
- The panel is rendered *outside* the tab switcher, not inside each tab

---

### `dashboard/src/components/guide/CommandBar.tsx` (UI component)

**Analog:** `dashboard/src/components/dashboard/CommandInput.tsx` — text input with submit button.

**Pattern:**
```typescript
interface CommandBarProps {
  onSend: (text: string) => void;
  onPark: () => void;
  loading?: boolean;
}

export function CommandBar({ onSend, onPark, loading }: CommandBarProps) {
  const [text, setText] = useState("");
  // ... debounced input, submit handler
}
```

---

### `dashboard/src/lib/api.ts` — EVOLVE (add guide endpoints)

**Analog:** `dashboard/src/lib/api.ts` itself — existing `apiGet`, `apiPost` patterns.

**Pattern:**
```typescript
export interface GuideCommandResponse {
  status: string;
  intent?: string;
  reply?: string;
  params?: Record<string, unknown>;
}

export async function sendGuideCommand(text: string): Promise<GuideCommandResponse> {
  return apiPost<GuideCommandResponse>("/api/v1/guide/command", { text });
}

export async function fetchGuideStatus(): Promise<{ metrics: Record<string, number> }> {
  return apiGet<{ metrics: Record<string, number> }>("/api/v1/guide/status");
}

export async function parkDistraction(text: string): Promise<{ status: string; entry_id?: string }> {
  return apiPost<{ status: string; entry_id?: string }>("/api/v1/guide/park", { text });
}
```

---

### `dashboard/src/hooks/useApi.ts` — EVOLVE (add guide hooks)

**Analog:** `dashboard/src/hooks/useApi.ts` itself — existing `useState` + `useCallback` + `useEffect` pattern.

**Pattern** (mirror `useEntrySynthesis` lines 127-159):
```typescript
export function useGuideCommand() {
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const send = useCallback(async (text: string) => {
    setLoading(true);
    setError("");
    try {
      const res = await sendGuideCommand(text);
      setReply(res.reply ?? "");
      return res;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed";
      setError(msg);
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  return { send, reply, loading, error };
}
```

---

## Shared Patterns

### `from __future__ import annotations` (all new `.py` files)
**Source:** `library.py` line 3, `cache.py` line 3, `deps.py` line 3.
**Apply to:** `search.py`, `intent_parser.py`, `guide.py`, all test files.

### `logger = logging.getLogger(__name__)` (all new `.py` files)
**Source:** `cache.py` line 11, `embed.py` line 13, `hooks.py` line 10.
**Apply to:** All new Python files.

### Private helper prefix `_`
**Source:** `router.py` `_detect_intent`, `_dispatch`; `cache.py` `_COSINE_THRESHOLD`.
**Apply to:** `search.py` → `_get_store` (if needed); `intent_parser.py` → `_INTENT_SYSTEM_PROMPT`.

### Parameterized SQL (no f-strings)
**Source:** `cache.py` lines 32-42; `hooks.py` lines 31-43.
**Apply to:** `search.py` — all SQL uses `%s` placeholders.

### `owner_id` scoping on every DB query
**Source:** `cache.py` `WHERE owner_id = %s`; `hooks.py` `WHERE owner_id = %s`.
**Apply to:** `search.py` — every query filters by `owner_id`.

### Absolute `src.` imports, never relative
**Source:** `library.py` `from src.api.deps import require_auth`; `cache.py` `from src.vector.db import get_pool`.
**Apply to:** All new Python files.

### React component patterns (dashboard)
**Source:** `EntryAIPanel.tsx`, `CommandInput.tsx`, `LinkCaptureModal.tsx`.
**Apply to:** All new guide components.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `dashboard/src/components/guide/AIGuidePanel.tsx` | layout / composite | render | No existing "persistent right-hand panel" component; built from existing sub-patterns |

---

## Metadata

**Analog search scope:** `solo-leveling/src/` + `dashboard/src/`
**Files read:** `src/vector/cache.py`, `src/vector/hooks.py`, `src/vector/embed.py`, `src/agents/dispatcher.py`, `src/core/router.py`, `src/api/library.py`, `src/api/v1_router.py`, `src/api/deps.py`, `src/app.py`, `dashboard/src/lib/api.ts`, `dashboard/src/hooks/useApi.ts`, `dashboard/src/components/dashboard/DashboardPage.tsx`, `dashboard/src/components/library/EntryAIPanel.tsx`
**Pattern extraction date:** 2026-05-30
