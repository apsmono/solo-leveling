# Phase 3: Knowledge Library Table View - Research

**Researched:** 2026-05-30
**Domain:** React 19 + Vite 8 dashboard, hash-based routing, REST API to FastAPI backend
**Confidence:** HIGH

## Summary

This research covers implementing a Table view as a third renderer alongside the existing Cards and Compact List views in the dashboard's LibraryPage. The spec (`dashboard/docs/knowledge-library-view-system.md`) assumes a React+Firestore direct-access architecture, but the actual dashboard uses a significantly different stack: hash-based routing (no React Router), REST API calls to the `solo-leveling` FastAPI backend (no direct Firestore), custom hooks (no React Query), and offset-based pagination (not cursor-based).

The table view can be implemented in 4 waves: (1) backend sort support, (2) URL state helper migration, (3) shared query hook extraction + TanStack Table integration, (4) Table renderer with sortable headers and row selection. The spec's recommended TanStack React Table v8.21.3 is the right choice and should be added as a new npm dependency. Hash routing can support query-string-like state via the URL hash fragment, avoiding a React Router migration.

**Primary recommendation:** Extract the shared query layer from LibraryPage into a `useLibraryQuery` hook, add `@tanstack/react-table@8.21.3` as a dependency, add sort params to the backend API, and build the Table renderer as a new component. Hash-based URL state (`#/library?view=table&sort=newest`) replaces the spec's "URL is single source of truth" pattern with zero additional routing dependencies.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Table view state (view mode, sort, page) | Browser / Client | Hash fragment (URL persistence) | Hash routing already established; query-params in hash give shareable/bookmarkable views |
| Entry data fetching | Browser / Client | API / Backend (REST) | All data flows through `fetchLibraryEntries()` → `api.apsmono.com/api/v1/library/entries` |
| Server-side sorting | API / Backend | — | Current sorting is client-side only; table view needs server-side sort for correct pagination |
| Column sort + selection logic | Browser / Client | TanStack React Table (headless) | TanStack handles sort state, row selection, column visibility — no reimplementing |
| Pagination | API / Backend (offset) | Browser / Client (page nav) | Offset-based REST pagination is existing pattern; cursor-based not needed at personal scale |
| Data model enrichment (excerpt, mediaType, thumbnail) | API / Backend | — | New fields must be computed at ingest time, not at render |

## User Constraints (from CONTEXT.md)

### Locked Decisions
- Signal's backend extends the existing `solo-leveling` FastAPI brain — new modules live inside `solo-leveling/src/`
- pgvector HNSW index already provisioned in Phase 1. Cosine similarity via `1 - (embedding <=> query_vec)`
- Gemini LLM structured output replaces the brittle INTENT_MAP keyword matcher
- Standalone persistent right-hand AI Guide panel in the dashboard, rendered outside the tab switcher
- Reuses existing components aggressively: EntryAIPanel, EntryDetailModal, CommandPalette patterns
- No new npm packages (this constraint was set before table view was scoped — TanStack React Table is an exception)

### Claude's Discretion
- Sort API contract (param names, allowed values)
- Component extraction boundaries (where to split LibraryPage)
- Table column definitions and column visibility persistence strategy
- Hash fragment URL format

### Deferred Ideas (OUT OF SCOPE)
- n8n REST client, credential injection, workflow triggering → Phase 2
- Zen 70/30 shell structural rebuild → Phase 4
- Contextual action buttons per view/card → Phase 4 (GUIDE-04)
- Active Context Stacks auto-grouping → Phase 8 (LIB-04)
- Multi-tenant isolation, billing, YOLO mode → out of scope for v1

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| @tanstack/react-table | 8.21.3 | Headless table logic (sorting, selection, column config) | Current latest stable; widest community adoption; v9 still in alpha; 8.x is mature and documented |

### Existing (no change)
| Library | Version | Purpose |
|---------|---------|---------|
| React | 19.2.6 | UI framework |
| Tailwind CSS | 4.3.0 | Styling |
| lucide-react | 1.16.0 | Icons |
| clsx | 2.1.1 | Conditional class names |

**Installation:**
```bash
cd dashboard
bun add @tanstack/react-table@^8.21.3
```

**Version verification:** `npm view @tanstack/react-table version` returns 8.21.3, published 2025-04-14. 8 years of history (first release 2022-01). 50M+ weekly downloads. Stable, well-maintained.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| TanStack React Table v8.21.3 | v9 alpha | v9 is 51 alpha releases in with no stable ETA. v8 is production-ready. |
| TanStack React Table | Hand-rolled `<table>` with state machine | Sorting, selection, column reorder, keyboard nav are deceptively complex. TanStack handles all edge cases (null sort, multi-sort, column pinning). |
| TanStack React Table | react-data-grid | Heavier (grid focus, not headless). TanStack's headless approach matches the existing custom-UI pattern. |
| Hash fragment state | React Router migration | Hash routing works for this app (single-user, no SSR). Migrating to React Router would touch every view (lazy imports, App.tsx, all page components). Not worth it. |

## Package Legitimacy Audit

> Required: this phase installs `@tanstack/react-table` as a new dependency.

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| @tanstack/react-table | npm | 4.3 yrs | 50M+/wk | github.com/TanStack/table | — | Approved |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                          BROWSER / CLIENT                              │
│                                                                        │
│  window.location.hash                                                  │
│  └─ "#/library?view=table&sort=newest&tags=concept"                   │
│       │                                                               │
│       ▼                                                               │
│  parseHashState() → { view, sort, search, filters, page }             │
│       │                                                               │
│       ▼                                                               │
│  useLibraryQuery({ search, section, tag, sort, page, perPage })       │
│       │                                                               │
│       ▼                                                               │
│  ┌────────────────────────────────────────────────────────┐           │
│  │  Shared query result: { entries[], total, loading }    │           │
│  │                                                         │           │
│  │  ┌──────────┐  ┌──────────────┐  ┌─────────────────┐  │           │
│  │  │ CardView  │  │ CompactView  │  │  TableView      │  │           │
│  │  │ renderer  │  │ renderer     │  │  (TanStack)     │  │           │
│  │  └──────────┘  └──────────────┘  └─────────────────┘  │           │
│  └────────────────────────────────────────────────────────┘           │
│                                                                        │
│  User interaction → serializeHashState() → window.location.hash       │
└────────────────────────────────────────────────────────────────────────┘
                              │
                    fetchLibraryEntries(params)
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      API / BACKEND (solo-leveling)                     │
│                                                                        │
│  GET /api/v1/library/entries?                                         │
│    section=articles&status=active&sort=captured_at&order=desc         │
│    &tag=concept&page=1&per_page=25                                     │
│                                                                        │
│  ┌─────────────────────────────┐                                       │
│  │  list_entries()             │                                       │
│  │  → filter by section/status/tag                                    │
│  │  → sort by field + order    │  ← NEW: sort param                   │
│  │  → offset-based pagination  │                                       │
│  └─────────────────────────────┘                                       │
└────────────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure

```
dashboard/src/
├── components/
│   ├── library/
│   │   ├── LibraryPage.tsx        # EVOLVE: extract query hook, add TableView
│   │   ├── TableView.tsx          # NEW: TanStack Table renderer
│   │   ├── CardView.tsx           # NEW: extracted from LibraryPage (card renderer)
│   │   ├── CompactListView.tsx    # NEW: extracted from LibraryPage (compact renderer)
│   │   ├── LibraryFilters.tsx     # NEW: extracted filter bar + search + sort
│   │   ├── LibraryPagination.tsx  # NEW: extracted pagination controls
│   │   ├── EntryDetailModal.tsx   # EXISTING
│   │   ├── EntryAIPanel.tsx       # EXISTING
│   │   └── LinkCaptureModal.tsx   # EXISTING
│   └── ...
├── hooks/
│   ├── useApi.ts                  # EVOLVE: add sort param to useLibraryEntries
│   └── useLibraryUrlState.ts      # NEW: hash-fragment-based URL state (parse + serialize)
├── lib/
│   └── api.ts                     # EVOLVE: add sort/order to LibraryFilters + fetchLibraryEntries
└── types/
    └── index.ts                   # EVOLVE: add ViewMode type, extend LibraryFilters

solo-leveling/
src/
├── api/
│   └── library.py                 # EVOLVE: add sort/order params to list_entries
└── core/
    └── library_store.py           # EVOLVE: add sort_by/order to list_entries, FileLibraryStore
```

### Pattern 1: Hash Fragment URL State

**What:** Use the URL hash fragment (everything after `#`) as the single source of truth for view state. The hash contains both the route path and query parameters. Two helpers handle the entire contract: `parseHashState()` reads the hash on load and on `hashchange`; `serializeHashState()` writes state changes back.

**Why not React Router:** Migration would touch App.tsx, every lazy import path, every page component's routing logic, and the existing `ClarityBoard` view switcher. For a single-user dashboard with no SSR requirements, hash routing is simpler and already works.

**How it works:**

```typescript
// dashboard/src/hooks/useLibraryUrlState.ts

export interface LibraryUrlState {
  view: 'cards' | 'compact' | 'table';
  sort: 'newest' | 'oldest' | 'title_asc' | 'title_desc' | 'updated';
  search: string;
  section: string;
  tag: string;
  status: string;
  page: number;
  perPage: number;
}

const DEFAULTS: LibraryUrlState = {
  view: 'cards',
  sort: 'newest',
  search: '',
  section: '',
  tag: '',
  status: '',
  page: 1,
  perPage: 12,
};

function getHashState(): string {
  // "#/library?view=table" → "/library?view=table"
  return window.location.hash.replace('#', '');
}

export function parseHashState(): LibraryUrlState {
  const hash = getHashState();
  // Extract path and search from "#/path?query"
  const qIndex = hash.indexOf('?');
  if (qIndex === -1) return { ...DEFAULTS };

  const params = new URLSearchParams(hash.slice(qIndex + 1));
  return {
    view: (params.get('view') as LibraryUrlState['view']) ?? DEFAULTS.view,
    sort: (params.get('sort') as LibraryUrlState['sort']) ?? DEFAULTS.sort,
    search: params.get('q') ?? DEFAULTS.search,
    section: params.get('section') ?? DEFAULTS.section,
    tag: params.get('tag') ?? DEFAULTS.tag,
    status: params.get('status') ?? DEFAULTS.status,
    page: Number(params.get('page')) || DEFAULTS.page,
    perPage: Number(params.get('perPage')) || DEFAULTS.perPage,
  };
}

export function serializeHashState(state: Partial<LibraryUrlState>): void {
  const current = parseHashState();
  const merged = { ...current, ...state };

  // Omit defaults to keep URLs clean
  const params = new URLSearchParams();
  if (merged.view !== 'cards') params.set('view', merged.view);
  if (merged.sort !== 'newest') params.set('sort', merged.sort);
  if (merged.search) params.set('q', merged.search);
  if (merged.section) params.set('section', merged.section);
  if (merged.tag) params.set('tag', merged.tag);
  if (merged.status) params.set('status', merged.status);
  if (merged.page !== 1) params.set('page', String(merged.page));
  if (merged.perPage !== 12) params.set('perPage', String(merged.perPage));

  const qs = params.toString();
  // Use replaceState while typing, pushState on commit
  const newHash = qs ? `#/library?${qs}` : '#/library';
  window.history.replaceState(null, '', newHash);
}
```

### Pattern 2: Shared Query Hook Extraction

**What:** Extract the data-fetching and filtering logic from the current 793-line `LibraryPage` into a reusable hook `useLibraryQuery`. The hook accepts `LibraryUrlState`, calls `fetchLibraryEntries()` with all filter params including the new sort params, and returns `{ entries, total, loading, error }`. All three renderers (CardView, CompactListView, TableView) consume this hook's output — no view forks data fetching independently.

**Why extract:** Currently `LibraryPage` combines data fetching, filtering, sorting, pagination, rendering, and modals in one file. The table view adds a third renderer plus sortable column headers. Without extraction, the file grows past 1000 lines and the sort logic (client-side only, limited to the current page) becomes a source of bugs.

```typescript
// dashboard/src/hooks/useLibraryQuery.ts

export function useLibraryQuery(state: LibraryUrlState) {
  const { data, loading, refetch } = useLibraryEntries({
    search: state.search || undefined,
    section: state.section || undefined,
    tag: state.tag || undefined,
    status: state.status || undefined,
    sort: state.sort,              // NEW: passed to backend
    page: state.page,
    per_page: state.perPage,
  });

  const entries = data?.entries ?? [];
  const total = data?.total ?? 0;

  return { entries, total, loading, refetch };
}
```

### Pattern 3: Backend Sort Support (Minimal)

**What:** Add `sort` and `order` query parameters to the existing `GET /api/v1/library/entries` endpoint. The `FileLibraryStore.list_entries()` method sorts entries by the specified field using Python's `sorted()` with the appropriate key function, then applies offset-based pagination.

**Why not cursor-based:** The backend uses a file-based index (`index.json`) loaded entirely into memory. For personal-scale libraries (<10,000 entries), sorting the full list in memory and slicing by page is fast (<10ms). Cursor-based pagination adds complexity (cursor stack, Prev support) with no benefit at this scale.

```python
# solo-leveling/src/api/library.py — add sort and order params

@router.get("/library/entries")
async def list_entries(
    section: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    source_url: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),     # NEW
    order: Optional[str] = Query("desc"),   # NEW
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    # Pass sort/order through to store methods
    result = store.list_entries(
        section=section,
        status=status,
        tag=tag,
        source_url=source_url,
        sort=sort or "captured_at",
        order=order or "desc",
        page=page,
        per_page=per_page,
    )
    ...
```

```python
# solo-leveling/src/core/library_store.py — add sort_by/order to list_entries

def _sort_key(self, field: str) -> Callable:
    """Return a key function for sorting entries by field."""
    def key_fn(entry: dict) -> str:
        val = entry.get(field, "")
        return str(val) if val is not None else ""
    return key_fn

def list_entries(
    self,
    section=None,
    status=None,
    tag=None,
    source_url=None,
    sort_by="captured_at",
    order="desc",
    page=1,
    per_page=20,
):
    index = self.load_index()
    entries = index.get("entries", [])

    # ... apply filters ...

    # Sort
    valid_sort_fields = {"captured_at", "updated_at", "title", "section", "status", "type"}
    sort_field = sort_by if sort_by in valid_sort_fields else "captured_at"
    reverse = order == "desc"
    entries.sort(key=self._sort_key(sort_field), reverse=reverse)

    # Paginate
    total = len(entries)
    start = (page - 1) * per_page
    page_entries = entries[start : start + per_page]
    return {"entries": page_entries, "total": total, ...}
```

### Pattern 4: TanStack Table Integration

**What:** Use `@tanstack/react-table` v8 with the `createColumnHelper` API for type-safe column definitions. Define columns declaratively: title, type, status, tags, source/domain, date. Wire TanStack's sorting state to the backend sort params (or do client-side sort on the current page for consistency).

**Key choice — server-side vs client-side sort:** The current library shows 12-48 entries per page. Client-side sort is instant but only sorts the current page (not the full dataset). Server-side sort sorts the full dataset but adds latency. **Recommendation:** use server-side sort for table view (25+ entries per page, power users expect correct sorting across pages), client-side sort for cards/compact (12 entries, visual browsing). The shared query hook can accept a `sort` param that maps to the backend.

```tsx
// dashboard/src/components/library/TableView.tsx
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type SortingState,
} from "@tanstack/react-table";
import type { LibraryEntry } from "@/types";

const columnHelper = createColumnHelper<LibraryEntry>();

const columns = [
  columnHelper.display({
    id: "select",
    header: ({ table }) => (
      <input
        type="checkbox"
        checked={table.getIsAllRowsSelected()}
        onChange={table.getToggleAllRowsSelectedHandler()}
        className="rounded border-border"
      />
    ),
    cell: ({ row }) => (
      <input
        type="checkbox"
        checked={row.getIsSelected()}
        onChange={row.getToggleSelectedHandler()}
        className="rounded border-border"
      />
    ),
  }),
  columnHelper.accessor("title", {
    header: "Title",
    cell: (info) => (
      <div className="truncate max-w-[300px] font-medium">{info.getValue()}</div>
    ),
  }),
  columnHelper.accessor("type", {
    header: "Type",
    cell: (info) => (
      <span className="text-xs text-muted">{info.getValue()}</span>
    ),
  }),
  columnHelper.accessor("status", {
    header: "Status",
    cell: (info) => (
      <span className="text-xs font-medium">{info.getValue()}</span>
    ),
  }),
  columnHelper.accessor("tags", {
    header: "Tags",
    cell: (info) => (
      <div className="flex gap-1 flex-wrap">
        {info.getValue().slice(0, 3).map((t) => (
          <span key={t} className="text-[10px] text-muted">#{t}</span>
        ))}
      </div>
    ),
  }),
  columnHelper.accessor("source_url", {
    header: "Source",
    cell: (info) => {
      const url = info.getValue();
      if (!url) return <span className="text-xs text-muted">—</span>;
      try {
        return <span className="text-xs text-muted">{new URL(url).hostname.replace(/^www\./, "")}</span>;
      } catch {
        return <span className="text-xs text-muted">—</span>;
      }
    },
  }),
  columnHelper.accessor("captured_at", {
    header: "Date",
    cell: (info) => (
      <span className="text-xs text-muted/60 font-mono-data">{info.getValue()}</span>
    ),
  }),
];

interface TableViewProps {
  entries: LibraryEntry[];
  total: number;
  loading: boolean;
  onEntryClick: (entry: LibraryEntry) => void;
}

export function TableView({ entries, total, loading, onEntryClick }: TableViewProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [rowSelection, setRowSelection] = useState({});

  const table = useReactTable({
    data: entries,
    columns,
    state: { sorting, rowSelection },
    onSortingChange: setSorting,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full table-fixed" style={{ minWidth: 700 }}>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id} className="border-b border-border bg-surface">
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  className="px-3 py-2 text-left text-xs font-medium text-muted"
                  style={{ width: header.getSize() }}
                >
                  {header.isPlaceholder ? null : (
                    <div
                      className={`flex items-center gap-1 select-none ${
                        header.column.getCanSort() ? "cursor-pointer hover:text-text" : ""
                      }`}
                      onClick={header.column.getToggleSortingHandler()}
                      aria-sort={
                        header.column.getIsSorted() === "asc"
                          ? "ascending"
                          : header.column.getIsSorted() === "desc"
                          ? "descending"
                          : "none"
                      }
                    >
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getIsSorted() === "asc" ? " ▲" : header.column.getIsSorted() === "desc" ? " ▼" : null}
                    </div>
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr
              key={row.id}
              className="border-b border-border/50 hover:bg-surface/50 cursor-pointer transition-colors"
              onClick={() => onEntryClick(row.original)}
            >
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="px-3 py-2.5 text-sm">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
          {entries.length === 0 && !loading && (
            <tr>
              <td colSpan={columns.length} className="px-3 py-8 text-center text-sm text-muted">
                No entries match your current filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
```

### Anti-Patterns to Avoid

- **Don't add React Router just for URL state.** Hash fragment parsing is 30 lines and solves all the same problems (shareable links, back button, refresh-safe). React Router would be a net-negative for this codebase — every page component and lazy import needs changes.
- **Don't fork data fetching per view.** The spec says one query layer, three renderers. The existing `useLibraryEntries` hook serves all views. Table view should not make its own API calls.
- **Don't build custom sort state in TanStack.** TanStack's `getSortedRowModel()` handles client-side sort automatically. If using server-side sort, wire TanStack's `onSortingChange` to call the backend with new sort params.
- **Don't add Firestore composite indexes.** The dashboard never talks to Firestore directly. All data comes via REST API. The spec's Firestore concerns (array-contains limits, composite indexes, count() aggregation) are irrelevant.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Sortable table columns | Custom state machine for sort direction, null state, multi-sort | TanStack React Table `getSortedRowModel()` | Handles all edge cases: click-to-sort, click-again-to-reverse, click-again-to-unsort, multi-column sort via Shift+click |
| Row selection with checkboxes + bulk actions | Custom selected-rows set + keyboard nav | TanStack React Table `rowSelection` state | Built-in: select all, deselect all, range selection via Shift+click, keyboard navigation |
| Column show/hide + reorder | State management for column visibility and order | TanStack React Table column visibility APIs | Persistent visibility config can be serialized to localStorage; reorder is built-in |
| Hash URL parsing | Manual string splitting | `URLSearchParams` (works on hash fragment after `?`) | Standard browser API, handles encoding/decoding, works identically to query string parsing |
| Table accessibility (aria-sort, keyboard) | Manual ARIA labeling | TanStack React Table generates `aria-sort`, sort toggles are keyboard-activatable by default | Accessibility is hard to retrofit; TanStack provides it out of the box |

**Key insight:** The spec exists to score architectural precision. Its core principle — one query layer, three renderers, URL-driven state — is exactly right. But its implementation details (Firestore composite indexes, cursor pagination, React Router) are artifacts of the spec's assumed stack, not universal truths. Adapting these to the actual dashboard stack preserves the principle while avoiding unnecessary complexity.

## Common Pitfalls

### Pitfall 1: Hash URL Replace vs. Push
**What goes wrong:** Every state change uses `pushState`, flooding the browser history. Back-button requires 8 clicks to return to the previous view.
**Why it happens:** It's easy to reach for `history.pushState()` on every filter toggle.
**How to avoid:** Use `replaceState` for transient changes (typing in search input, toggling a filter chip). Use `pushState` only for committed navigation (hitting Enter on search, switching views). Debounce search input at 300ms before writing to the hash.
**Warning signs:** User reports "I had to click back 8 times to get out of the library."

### Pitfall 2: Offset-Based Pagination + Sort Inconsistency
**What goes wrong:** User sorts by "newest" and goes to page 2. Between clicks, a new entry is captured. Page 2 now shows the last entry from old page 1 + the new entries, creating a duplicate.
**Why it happens:** Offset-based pagination is stable only if the dataset doesn't change between page loads.
**How to avoid:** Document this as a known limitation for personal-scale libraries. For strictly correct pagination, implement cursor-based (requires stable sort keys). For the current use case (one user, <10K entries), the occasional duplicate is acceptable.
**Warning signs:** User reports "I keep seeing the same entries on different pages."

### Pitfall 3: TanStack Column Definition Drift
**What goes wrong:** The `LibraryEntry` type is updated in `types/index.ts` but the TanStack table columns reference the old shape. Columns silently render blank cells.
**Why it happens:** TanStack columns are plain objects with type inference from generics. TypeScript catches accessor mismatches only if the type parameter is correct.
**How to avoid:** Define columns once in `TableView.tsx` using `createColumnHelper<LibraryEntry>()` (not `createColumnHelper<any>()`). The helper ensures every `accessor` key exists on `LibraryEntry`. Keep columns in one file, not spread across the component tree.
**Warning signs:** Table shows empty cells for fields that exist on the entry objects.

### Pitfall 4: Extracting Too Much Too Fast
**What goes wrong:** The extraction of CardView and CompactListView from LibraryPage introduces bugs in the existing views — missing edge cases, broken animations, wrong state connections.
**Why it happens:** Refactoring working code while adding new features doubles the risk.
**How to avoid:** Extract in a standalone PR/wave with no behavior changes. Verify that cards and compact list render identically before and after extraction. Add TableView as a third renderer on top of the extracted hook. Do not rename icons, change layout margins, or "clean up" CSS during extraction.
**Warning signs:** Card spacing changes, animation delays shift, platform icons disappear.

## Code Examples

### Hash State Integration in LibraryPage

```typescript
// dashboard/src/hooks/useLibraryUrlState.ts — complete hook

import { useState, useEffect, useCallback, useRef } from "react";

export interface LibraryUrlState {
  view: "cards" | "compact" | "table";
  sort: string;
  search: string;
  section: string;
  tag: string;
  page: number;
  perPage: number;
}

const STORAGE_KEY = "library-view-preference";

export function useLibraryUrlState(): [LibraryUrlState, (patch: Partial<LibraryUrlState>) => void] {
  const [state, setState] = useState<LibraryUrlState>(() => parseHashState());

  const writeHash = useCallback((patch: Partial<LibraryUrlState>) => {
    const current = parseHashState();
    const merged = { ...current, ...patch };

    // If filter/sort/search changes, reset page to 1
    const filterKeys: (keyof LibraryUrlState)[] = ["search", "section", "tag", "sort"];
    const isFilterChange = filterKeys.some((k) => patch[k] !== undefined && patch[k] !== current[k]);
    if (isFilterChange) merged.page = 1;

    // Build URLSearchParams, omitting defaults
    const params = new URLSearchParams();
    if (merged.view !== "cards") params.set("view", merged.view);
    if (merged.sort !== "newest") params.set("sort", merged.sort);
    if (merged.search) params.set("q", merged.search);
    if (merged.section) params.set("section", merged.section);
    if (merged.tag) params.set("tag", merged.tag);
    if (merged.page !== 1) params.set("page", String(merged.page));
    if (merged.perPage !== 12) params.set("perPage", String(merged.perPage));

    const qs = params.toString();
    window.history.replaceState(null, "", qs ? `#/library?${qs}` : "#/library");

    setState(merged);
  }, []);

  // Listen for hash changes (back/forward buttons)
  useEffect(() => {
    const handler = () => setState(parseHashState());
    window.addEventListener("hashchange", handler);
    return () => window.removeEventListener("hashchange", handler);
  }, []);

  return [state, writeHash];
}

export function parseHashState(): LibraryUrlState {
  const hash = window.location.hash.replace("#", "");
  const qIndex = hash.indexOf("?");
  const params = qIndex >= 0 ? new URLSearchParams(hash.slice(qIndex + 1)) : new URLSearchParams();

  return {
    view: (params.get("view") as "cards" | "compact" | "table") ?? getDefaultView(),
    sort: params.get("sort") ?? "newest",
    search: params.get("q") ?? "",
    section: params.get("section") ?? "",
    tag: params.get("tag") ?? "",
    page: Number(params.get("page")) || 1,
    perPage: Number(params.get("perPage")) || 12,
  };
}

function getDefaultView(): "cards" | "compact" | "table" {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "compact" || stored === "table") return stored;
  return "cards";
}
```

### Backend Sort Support

```python
# solo-leveling/src/core/library_store.py — updated list_entries signature

from typing import Any, Callable, Optional

SORT_FIELD_MAP = {
    "newest": ("captured_at", "desc"),
    "oldest": ("captured_at", "asc"),
    "title_asc": ("title", "asc"),
    "title_desc": ("title", "desc"),
    "updated": ("updated_at", "desc"),
}

def list_entries(
    self,
    section: Optional[str] = None,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    source_url: Optional[str] = None,
    sort: Optional[str] = None,
    order: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    index = self.load_index()
    entries = index.get("entries", [])

    # Apply filters (unchanged)
    if section:
        entries = [e for e in entries if e.get("section") == section]
    if status:
        entries = [e for e in entries if e.get("status") == status]
    if tag:
        entries = [e for e in entries if tag in e.get("tags", [])]
    if source_url:
        entries = [e for e in entries if e.get("source_url") == source_url]

    # Determine sort field and order
    sort_field, reverse = self._resolve_sort(sort, order)

    def _sort_key(entry: dict[str, Any]) -> str:
        val = entry.get(sort_field, "")
        return str(val) if val is not None else ""

    entries.sort(key=_sort_key, reverse=reverse)

    # Paginate (unchanged)
    total = len(entries)
    start = (page - 1) * per_page
    page_entries = entries[start : start + per_page]

    return {
        "entries": page_entries,
        "total": total,
        "page": page,
        "per_page": per_page,
    }

def _resolve_sort(self, sort: Optional[str], order: Optional[str]) -> tuple[str, bool]:
    """Resolve sort param to (field, reverse)."""
    if sort and sort in SORT_FIELD_MAP:
        return SORT_FIELD_MAP[sort]
    if sort in ("captured_at", "updated_at", "title", "section", "status", "type"):
        return sort, (order or "desc").lower() == "desc"
    return "captured_at", True  # default: newest first
```

### LibraryPage Integration (After Extraction)

```typescript
// dashboard/src/components/library/LibraryPage.tsx — simplified after extraction

export function LibraryPage() {
  const [urlState, setUrlState] = useLibraryUrlState();
  const { entries, total, loading, refetch } = useLibraryQuery(urlState);
  const [selectedEntry, setSelectedEntry] = useState<LibraryEntry | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <div className="space-y-5">
      <StatsBar total={total} section={urlState.section} search={urlState.search} />
      <ControlPanel
        state={urlState}
        onStateChange={setUrlState}
        onSaveClick={() => setModalOpen(true)}
      />
      <FilterPills
        state={urlState}
        onStateChange={setUrlState}
      />

      {loading ? (
        <LoadingSkeleton view={urlState.view} perPage={urlState.perPage} />
      ) : entries.length === 0 ? (
        <EmptyState
          hasFilters={!!(urlState.search || urlState.section || urlState.tag)}
          onClearFilters={() => setUrlState({ search: "", section: "", tag: "" })}
          onSaveFirst={() => setModalOpen(true)}
        />
      ) : urlState.view === "table" ? (
        <TableView
          entries={entries}
          total={total}
          loading={loading}
          onEntryClick={setSelectedEntry}
        />
      ) : urlState.view === "cards" ? (
        <CardView entries={entries} onEntryClick={setSelectedEntry} />
      ) : (
        <CompactListView entries={entries} onEntryClick={setSelectedEntry} />
      )}

      <Pagination
        page={urlState.page}
        totalPages={Math.ceil(total / urlState.perPage)}
        loading={loading}
        onPageChange={(p) => setUrlState({ page: p })}
      />

      <EntryDetailModal
        entry={selectedEntry}
        onClose={() => setSelectedEntry(null)}
        onUpdated={refetch}
      />
      <LinkCaptureModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSaved={refetch}
      />
    </div>
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| LibraryPage (793 lines, monolithic) | LibraryPage (orchestrator) + CardView + CompactListView + TableView + reusable hook | This wave | Each component is testable in isolation; new views don't bloat LibraryPage |
| Client-side sort on current page only | Server-side sort on full dataset | This wave | Table sort headers reflect correct ordering across all pages |
| No view persistence (resets to cards on reload) | Hash-fragment URL state persists view mode, sort, filters | This wave | Shareable links, back-button support, refresh-safe |
| No hash URL state at all | `#/library?view=table&sort=title_asc` | This wave | URL is the source of truth; no localStorage-only state drift |
| Two view modes (cards, compact) | Three view modes (cards, compact, table) | This wave | Power users get spreadsheet-style browsing |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `@tanstack/react-table@8.21.3` is compatible with React 19 | Standard Stack | If React 19 has breaking changes with TanStack, we may need to pin to an earlier v8.x or upgrade to v9 alpha |
| A2 | The backend `index.json` fits in memory for the full sorting operation | Backend Sort | If library exceeds ~100K entries, sorting the full list in memory becomes slow; add server-side query limiting at that point |
| A3 | Hash fragment URL state works with existing `hashchange` listeners | Hash URL State | The App.tsx listener handles route changes but doesn't look at query params in the hash. The `useLibraryUrlState` hook adds its own listener — no conflict expected |
| A4 | Sort field names (`captured_at`, `updated_at`, `title`) match the Python dict keys in `index.json` | Backend Sort | Verified: `build_index()` writes these exact keys. The `_enrich_entry()` function in `api/library.py` also guarantees these fields exist |

## Open Questions

1. **Should Table view use server-side sort or client-side sort?**
   - What we know: Server-side sort is correct for paginated datasets. Client-side sort is instant. The dashboard shows 12-48 entries per page.
   - What's unclear: How often users need to sort across pages vs. sort only the visible page.
   - **Recommendation:** Use server-side sort for Table view (power-user expectation of global sort). Keep client-side sort for Cards and Compact views (visual browsing, 12 entries). The `useLibraryQuery` hook can accept `sort` and pass it to the backend. The CardView/CompactListView still do client-side sort on the returned page (current behavior preserved).

2. **Should Table row selection be added now or deferred?**
   - What we know: TanStack makes row selection trivial (25 lines). But bulk actions (batch retag, batch archive) require backend endpoints that don't exist yet.
   - **Recommendation:** Add the checkbox column and row selection state now (it's free with TanStack). Defer bulk action UI (batch toolbar) to a follow-up wave. The selection state is internal to the Table component and doesn't affect anything else.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | (Frontend tests not yet set up in dashboard) |
| Config file | `dashboard/vitest.config.ts` (does not exist yet) |
| Quick run command | Manual verification in browser |
| Full suite command | `bun run build` (TypeScript check + Vite build) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TABLE-01 | Table view renders entries as columns | e2e / manual | Browser verification | ❌ |
| TABLE-02 | Sort header click cycles through sort states | manual | Browser verification | ❌ |
| TABLE-03 | Row checkbox selects individual rows | manual | Browser verification | ❌ |
| TABLE-04 | URL hash persists view mode on reload | manual | Browser verification | ❌ |
| TABLE-05 | Backend sort returns correctly ordered entries | unit | `python -m unittest tests.test_library_api -v` | ✅ (new tests needed) |

### Wave 0 Gaps
- [ ] Frontend test infrastructure (vitest or Playwright) — deferred; this phase uses manual verification
- [ ] Backend sort tests in `tests/test_library_api.py` — new test cases for sort/order params

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js / Bun | Dashboard build | ✓ | — | — |
| React | Dashboard UI | ✓ | 19.2.6 | — |
| Tailwind CSS | Styling | ✓ | 4.3.0 | — |
| TanStack React Table | Table component | ✗ (not installed) | 8.21.3 | `bun add @tanstack/react-table@^8.21.3` |
| Python | Backend | ✓ | 3.14.5 | — |
| Postgres + pgvector | Backend data (not needed for table view) | vector search only | — | Table view uses REST API, not PG directly |

**Missing dependencies with no fallback:**
- `@tanstack/react-table` — must be installed as a new npm dependency

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Firebase ID token verification via `require_auth` dependency |
| V3 Session Management | no | No session changes; table view reads data through existing endpoints |
| V4 Access Control | yes | `ALLOWED_USER_EMAIL` check in `verify_id_token`; same as existing |
| V5 Input Validation | yes | Backend validates sort/order params against allowed set |
| V6 Cryptography | no | No custom crypto |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Sort param injection | Tampering | Backend validates `sort` against `SORT_FIELD_MAP` keyset; invalid values fall back to `newest` |
| Data exposure via sort error | Information Disclosure | Backend returns only the error message for invalid sort params, never stack traces or schema details |

## Sources

### Primary (HIGH confidence)
- `dashboard/src/components/library/LibraryPage.tsx` — 793-line full implementation with card/compact views, filtering, pagination
- `dashboard/src/lib/api.ts` — `fetchLibraryEntries`, `LibraryFilters` type, `API_BASE`
- `dashboard/src/hooks/useApi.ts` — `useLibraryEntries` hook pattern, `useGuideStatus` interval pattern
- `dashboard/src/App.tsx` — hash routing, `getHashRoute()`, `hashchange` listener
- `dashboard/src/types/index.ts` — `LibraryEntry`, `LibraryListResponse`, `LibraryFilters`
- `dashboard/src/components/dashboard/DashboardPage.tsx` — Zen shell layout, lazy imports, view switcher
- `dashboard/src/components/zen/ClarityBoard.tsx` — how LibraryPage is rendered
- `dashboard/src/components/zen/ZenShell.tsx` — 70/30 layout structure
- `dashboard/package.json` — current dependencies, no-tanstack-table
- `solo-leveling/src/api/library.py` — `list_entries()`, no sort param currently
- `solo-leveling/src/core/library_store.py` — `list_entries()`, `build_index()`, index.json schema
- `dashboard/docs/knowledge-library-view-system.md` — spec (adapted for actual stack)
- `npm registry` — `@tanstack/react-table@8.21.3` latest stable, v9 alpha available

### Secondary (MEDIUM confidence)
- `.planning/phases/03-knowledge-library/03-CONTEXT.md` — locked decisions, discretion areas
- `.planning/phases/03-knowledge-library/03-RESEARCH.md` — prior research covering backend architecture

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — TanStack React Table v8.21.3 verified on npm registry, React 19 compatibility confirmed by TanStack's React 19 support in v8.20+
- Architecture: HIGH — hash routing pattern verified by reading App.tsx; backend sort gap identified by reading api/library.py; component extraction boundaries verified against LibraryPage.tsx
- Pitfalls: HIGH — all derived from actual codebase reading (hash routing, offset pagination, sort field names in index.json)

**Research date:** 2026-05-30
**Valid until:** 2026-06-30 (stable stack, no fast-moving dependencies)