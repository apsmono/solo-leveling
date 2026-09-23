---
phase: 03-knowledge-library
plan: 06-01
subsystem: api
tags: [sort, pagination, fastapi, query-params, library]

requires:
  - phase: 03-knowledge-library
    provides: "Library store with list_entries pagination and search"
provides:
  - "SORT_FIELD_MAP with named sort shortcuts (newest, oldest, title_asc, title_desc, updated)"
  - "sort/order query params on GET /api/v1/library/entries"
  - "Client-side sort in search path before pagination"
  - "Server-side sort in non-search path via store.list_entries"
affects: [03-knowledge-library, dashboard-table-view]

tech-stack:
  added: []
  patterns: ["Named sort shortcuts mapped to (field, reverse) tuples", "Invalid sort silently falls back to default"]

key-files:
  created: []
  modified:
    - solo-leveling/src/core/library_store.py
    - solo-leveling/src/api/library.py
    - solo-leveling/tests/test_library_api.py
    - solo-leveling/CHANGELOG.md

key-decisions:
  - "SORT_FIELD_MAP defines named shortcuts; raw field names also accepted with order override"
  - "Invalid sort params fall back to default (newest first) without error — no traceback or schema leak"

patterns-established:
  - "Sort contract: named shortcuts in SORT_FIELD_MAP, raw field names with order override, default fallback"

requirements-completed: [TABLE-01]

duration: 15min
completed: 2026-05-30
---

# Phase 3 Plan 6-01: Table View Backend Sort Summary

**Server-side sort for library entries with named shortcuts (newest/oldest/title_asc/title_desc/updated) and raw field name override via sort/order query params**

## Performance

- **Duration:** 15 min
- **Started:** 2026-05-30T09:49:44Z
- **Completed:** 2026-05-30T10:05:22Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- Added SORT_FIELD_MAP constant and _resolve_sort helper to library_store.py for mapping named sort shortcuts to (field, reverse) tuples
- Updated list_entries endpoint with sort/order Query params, applied before pagination in both search and non-search code paths
- Added 4 new test cases covering sort by newest, title ascending, invalid param fallback, and sort-with-search interaction

## Task Commits

Each task was committed atomically:

1. **Task 1: Add sort/order support to _FileLibraryStore.list_entries** - `0594a3d` (feat)
2. **Task 2: Add sort/order query params to GET /library/entries endpoint** - `b058dd5` (feat)
3. **Task 3: Add test cases for sort/order params** - `e0a1585` (test)

**Plan metadata:** `9bb4edc` (docs: update CHANGELOG)

## Files Created/Modified
- `solo-leveling/src/core/library_store.py` - SORT_FIELD_MAP constant, _resolve_sort static method, updated list_entries signatures (abstract + File + Firestore stores)
- `solo-leveling/src/api/library.py` - Added sort/order Query params, _resolve_sort_param helper for search path, SORT_FIELD_MAP import
- `solo-leveling/tests/test_library_api.py` - 4 new sort test cases (newest, title_asc, invalid_fallback, sort_with_search)
- `solo-leveling/CHANGELOG.md` - Added changelog entry for sort support

## Decisions Made
- Named sort shortcuts (newest, oldest, title_asc, title_desc, updated) are the primary interface; raw field names (captured_at, title, updated_at, section, status, type) accepted with order override
- Invalid/unknown sort params silently fall back to default (newest first) without error — aligns with threat model T-03-23 (Information Disclosure accepted)
- Sort is applied before pagination in both code paths to ensure correct per-page ordering

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Backend sort support complete for Table View frontend consumption
- Dashboard Table View can now pass sort/order params to GET /api/v1/library/entries
- Requirement TABLE-01 verified

---
*Phase: 03-knowledge-library*
*Completed: 2026-05-30*

## Self-Check: PASSED

- SUMMARY.md: FOUND
- Commit 0594a3d (Task 1): FOUND
- Commit b058dd5 (Task 2): FOUND
- Commit e0a1585 (Task 3): FOUND
- Commit 9bb4edc (CHANGELOG): FOUND
- library_store.py: FOUND
- library.py: FOUND
- test_library_api.py: FOUND
