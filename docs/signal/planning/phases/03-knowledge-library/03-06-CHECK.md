---
phase: 03-knowledge-library
plan: 06
check_type: plan-revision
status: issues_found
generated: 2026-05-30
revision: 2
---

# Plan Re-Check: Phase 3 Plan 06 -- Table View in Knowledge Library

## VERDICT: ISSUES FOUND

**Phase:** 03-knowledge-library (Plan 06: Table View)
**Plans checked:** 5 (1 orchestrator + 4 sub-plans)
**Issues:** 1 blocker(s), 1 warning(s), 1 info
**Previous check blockers addressed:** 2 of 3

---

## Fix Verification

### Fix 1: libraryHelpers.ts in files_modified -- RESOLVED

`libraryHelpers.ts` is now listed in `files_modified` frontmatter of both:
- `03-06-PLAN.md` (orchestrator) line 16
- `03-06-03-PLAN.md` line 9

### Fix 2: Verification command uses `bun run build` -- RESOLVED

All `<automated>` verify commands across all plans use `bun run build`. The orchestrator verification section (line 190) now reads:
```
cd dashboard && bun run build && bun run preview
```

No `bunx vite build` remains in any automated command.

### Fix 3: CardView + CompactListView merged into single task -- PARTIALLY RESOLVED

Task 2 in 03-06-03 now covers both CardView.tsx and CompactListView.tsx in a single task. However, the **total auto task count is still 5, not 4** as claimed:

| Task | Name | Type |
|------|------|------|
| 1 | Extract helper functions into libraryHelpers.ts | auto |
| 2 | Create CardView.tsx + CompactListView.tsx (merged) | auto |
| 3 | Create LibraryFilters.tsx | auto |
| 4 | Create LibraryPagination.tsx | auto |
| 5 | Refactor LibraryPage.tsx into an orchestrator | auto |
| 7 | Human verification -- visual regression check | checkpoint:human-verify |

The merge of CardView+CompactListView saved one task slot, but Task 5 (Refactor LibraryPage) exists as a separate auto task, keeping the total at 5. The scope_sanity threshold remains: 5+ auto tasks = BLOCKER.

---

## Dimension-by-Dimension Analysis

### Dimension 1: Requirement Coverage -- PASS

| Requirement | Covered By | Status |
|-------------|-----------|--------|
| TABLE-01: Backend sort params (sort/order) in GET /api/v1/library/entries | 03-06-01 | Covered |
| TABLE-02: URL hash maintains view/sort/filter state | 03-06-02 | Covered |
| TABLE-03: Cards/Compact views render identically after extraction | 03-06-03 | Covered |
| TABLE-04: Table view renders entries with sortable columns using TanStack | 03-06-04 | Covered |
| TABLE-05: bun run build passes (TypeScript check) | Cross-cutting, all plans | Covered |

### Dimension 2: Task Completeness -- PASS

All tasks have required elements (files, action, verify, done).

### Dimension 3: Dependency Correctness -- PASS

Linear chain: 03-06-01 (Wave 1) -> 03-06-02 (Wave 2) -> 03-06-03 (Wave 3) -> 03-06-04 (Wave 4). No cycles.

### Dimension 4: Key Links Planned -- PASS

All key_links from must_haves are covered by task actions.

### Dimension 5: Scope Sanity -- BLOCKER

| Plan | Auto Tasks | Checkpoints | Files | Verdict |
|------|-----------|-------------|-------|---------|
| 03-06-01 | 3 | 0 | 4 | OK |
| 03-06-02 | 4 | 0 | 5 | Warning |
| 03-06-03 | **5** | 1 | 6 | **BLOCKER** |
| 03-06-04 | 2 | 1 | 3 | OK |

Plan 03-06-03 still has 5 auto tasks. The merge of CardView+CompactListView was applied, but a separate Task 5 (Refactor LibraryPage) was kept, maintaining the count at 5.

### Dimension 6: Verification Derivation -- PASS

Truths are user-observable. Artifacts map to truths. Key links connect artifacts.

### Dimension 7: Context Compliance -- PASS

No CONTEXT.md decisions contradicted.

### Dimension 7b: Scope Reduction -- PASS

No scope-reduction language found.

### Dimension 7c: Architectural Tier Compliance -- PASS

All plans assign capabilities to the correct tier per RESEARCH-TABLE-VIEW.md.

### Dimension 8: Nyquist Compliance -- PASS

All tasks have `<automated>` verify commands. No MISSING references.

### Dimension 9: Cross-Plan Data Contracts -- PASS

Sort/order data flows consistently across all 4 plans.

### Dimension 10: CLAUDE.md Compliance -- PASS

Build and test conventions followed.

### Dimension 11: Research Resolution -- WARNING (carried from previous check)

`03-RESEARCH-TABLE-VIEW.md` Open Questions section at line 808 lacks `(RESOLVED)` suffix. Content is substantively resolved but marker format is missing.

### Dimension 12: Pattern Compliance -- SKIPPED

PATTERNS.md does not cover Table View files (generated before this wave was scoped).

---

## Issues Found

### Blockers (must fix)

**1. [scope_sanity] Plan 03-06-03 still has 5 auto tasks -- exceeds threshold**

- Plan: 03-06-03
- Metrics: 5 auto tasks + 1 checkpoint + 6 file modifications
- Description: The merge of CardView+CompactListView (Task 2) was applied correctly, but the plan retains 5 auto tasks because Task 5 (Refactor LibraryPage.tsx) exists as a separate auto task. The scope_sanity threshold is 2-3 target, 4 warning, 5+ blocker.
- Fix: Merge Task 4 (LibraryPagination.tsx) and Task 5 (Refactor LibraryPage.tsx) into a single task. LibraryPagination is a small extraction (~80 lines) and the LibraryPage refactor must reference it anyway. Combining them brings auto task count to 4 (warning level, not blocker). Alternatively, merge Task 1 (libraryHelpers.ts, ~90 lines) into Task 2 (CardView+CompactListView) since both CardView and CompactListView import from libraryHelpers -- extracting helpers as the first step of the view component task is natural.

### Warnings (should fix)

**1. [research_resolution] 03-RESEARCH-TABLE-VIEW.md Open Questions lacks (RESOLVED) suffix** (carried)

- File: `03-RESEARCH-TABLE-VIEW.md`
- Fix: Rename `## Open Questions` to `## Open Questions (RESOLVED)`. Add `**RESOLVED:**` markers.

### Info (suggestions)

**1. [task_numbering] Task numbering gap: Tasks go 1, 2, 3, 4, 5, 7**

- Plan: 03-06-03
- Description: No Task 6. The checkpoint jumped from Task 5 to Task 7. Minor cosmetic issue.
- Fix: Renumber checkpoint to Task 6.

---

## Recommendation

**1 blocker remains.** The CardView+CompactListView merge was applied but did not reduce the auto task count below 5 because Task 5 (Refactor LibraryPage) is a separate auto task.

**Quickest fix:** Merge Task 1 (libraryHelpers.ts) into Task 2 (CardView+CompactListView). The helpers file is a prerequisite for both view components -- extracting it as the first step of the combined view task is natural and reduces auto tasks from 5 to 4.
