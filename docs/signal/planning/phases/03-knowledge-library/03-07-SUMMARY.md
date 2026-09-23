---
phase: 03-knowledge-library
plan: "07"
subsystem: ui
tags: [react, typescript, vite, vitest, hash-routing, spa, dashboard]

# Dependency graph
requires:
  - phase: 03-knowledge-library
    provides: Library page with useLibraryUrlState writing #/library?... hash to browser URL
provides:
  - routeToTabState pure helper — shared route→tab-state mapping for all dashboard-owned hash routes
  - tabStateToRoute pure helper — inverse write-side mapping for tab→URL hash sync
  - App.tsx router that sends all dashboard-owned paths to DashboardPage and NotFound for unknown routes
  - DashboardPage that hydrates zenView/moreTab from URL hash on mount (deep-link/refresh support)
  - In-app tab→URL sync: every dashboard tab switch updates the browser hash
affects:
  - 03-knowledge-library (UAT items 9–13 unblocked once backend data present)
  - Any future plan adding new dashboard tabs (must extend dashboardRoutes.ts)

# Tech tracking
tech-stack:
  added:
    - vitest@4.1.7 (no test runner existed in dashboard; added to support TDD on routeToTabState)
  patterns:
    - Route helper as single source of truth: one pure module (dashboardRoutes.ts) defines the mapping both App.tsx router and DashboardPage initializer share — no divergence risk
    - Lazy useState initializer for URL hydration: routeToTabState(window.location.hash) called once inside useState(() => ...) on mount, not in useEffect, avoiding a render cycle
    - Write-side inverse: tabStateToRoute mirrors routeToTabState so that in-app tab switches push matching URL hashes without duplicating mapping logic

key-files:
  created:
    - dashboard/src/lib/dashboardRoutes.ts
    - dashboard/src/lib/dashboardRoutes.test.ts
  modified:
    - dashboard/src/App.tsx
    - dashboard/src/components/dashboard/DashboardPage.tsx

key-decisions:
  - "Added vitest@4.1.7 dev dependency — no test runner existed; needed for TDD on routeToTabState helper"
  - "Scope extension approved mid-checkpoint: added tabStateToRoute (write-side) beyond original read-only routing fix so in-app tab changes also update the URL hash"
  - "Bug fix for Core Dashboard tab (stale moreTab written as hash) and Knowledge Library tab (over-delegated null) during tabStateToRoute wiring"
  - "Do NOT change the #/library?... hash format written by useLibraryUrlState — only App.tsx/DashboardPage adapt to recognize it; CommandPalette deep-links depend on the existing format"
  - "UAT items 9–13 deferred to post-deploy human testing — local environment had no data; these are not this plan's must_haves"

patterns-established:
  - "dashboardRoutes.ts: centralized route-tab mapping — extend this file when adding new dashboard tabs; do not inline mapping in App.tsx or DashboardPage"
  - "tabStateToRoute + routeToTabState are inverses; keep them in sync in dashboardRoutes.ts"
  - "App.tsx switch-true pattern: /view* first, /login second, routeToTabState non-null third, default NotFound — preserve this order"

requirements-completed: [LIB-01, LIB-02, LIB-03, LIB-05]

# Metrics
duration: ~45min (implementation + human UAT checkpoint)
completed: "2026-05-30"
---

# Phase 03 Plan 07: Hash-Route Deep-Link and Tab-URL Sync Summary

**Pure routeToTabState/tabStateToRoute helpers + App.tsx router fix + DashboardPage hash hydration close the UAT item-8 deep-link/refresh blocker and add full in-app tab-to-URL sync for all dashboard tabs**

## Performance

- **Duration:** ~45 min (execution + human-verify checkpoint)
- **Started:** 2026-05-30T~10:30Z
- **Completed:** 2026-05-30
- **Tasks:** 4 (Tasks 1, 2, 3, 3b scope extension, plus bug fix, plus Task 4 push/bump)
- **Files modified:** 4 source files + 1 new test file

## Accomplishments

- Created `dashboardRoutes.ts` with two pure helpers (`routeToTabState`, `tabStateToRoute`) as the single source of truth for all dashboard-owned hash routes
- Fixed App.tsx router: all dashboard-owned paths (`/library`, `/planning`, `/overview`, `/graph`, `/timeline`, `/analysis`, `/calendar`, `/commands`, `/reminders`, `/`) now route to DashboardPage; only genuinely unknown routes reach NotFound
- Fixed DashboardPage: `zenView`/`moreTab` state hydrated from URL hash on mount via lazy useState initializer — refresh and deep-link now land on the correct tab
- Added in-app tab→URL hash sync (scope extension approved mid-checkpoint): switching tabs inside the dashboard now updates the browser hash so the URL is always shareable
- vitest test suite: 30/30 passing including all routeToTabState and tabStateToRoute cases
- `bun run build` clean (TS typecheck + Vite bundle)
- Human-verified: item 8 fixed (refresh/deep-link to #/library renders Library, not 404); in-app tab→URL sync confirmed for Core `/`, Library `/library`, Planner `/planning`, and more-tabs

## Task Commits

All commits are inside the `dashboard/` submodule on branch `feat/03-06-02-table-view-foundation`:

1. **Task 1 (RED):** routeToTabState failing tests — `efeb471` (test)
2. **Task 1 (GREEN):** routeToTabState implementation — `19c0097` (feat)
3. **Task 2:** App.tsx router restructure — `1477c3d` (fix)
4. **Task 3:** DashboardPage lazy useState hash hydration — `66e987b` (fix)
5. **Task 3b (RED):** tabStateToRoute failing tests — `590fe03` (test)
6. **Task 3b (GREEN):** tabStateToRoute implementation — `85e6c47` (feat)
7. **Task 3b wiring:** hook tabStateToRoute into DashboardPage tab handlers — `8902ccf` (fix)
8. **Bug fix:** correct URL hash for Core Dashboard + Knowledge Library tabs — `da39e58` (fix)
9. **Task 4 — parent bump:** `e661794` — `chore: bump dashboard — Phase 3 hash-route deep-link/refresh + tab→URL sync fix`

**Plan metadata commit:** (this SUMMARY + STATE/ROADMAP update)

## Files Created/Modified

- `dashboard/src/lib/dashboardRoutes.ts` — Pure `routeToTabState` and `tabStateToRoute` helpers; defines the canonical route allow-list for all dashboard-owned hash paths
- `dashboard/src/lib/dashboardRoutes.test.ts` — 30-case vitest suite covering all mapping paths, unknowns, query-string stripping, and inverse round-trips
- `dashboard/src/App.tsx` — Restructured switch-true router; third arm uses `routeToTabState(route) !== null` to send dashboard paths to DashboardPage; default arm is now genuinely unknown routes only
- `dashboard/src/components/dashboard/DashboardPage.tsx` — Lazy `useState` initializers read `routeToTabState(window.location.hash)` on mount; tab-change handlers call `tabStateToRoute` to sync URL hash

## Decisions Made

- Added vitest@4.1.7 as a dev dependency — no test runner existed in the dashboard project; needed for TDD on the route helper
- Scope extension approved by user mid-checkpoint: added tabStateToRoute (write-side inverse) so in-app tab switches also update the browser URL hash; this goes beyond the original read-only routing fix but was explicitly approved
- Bug fix for Core Dashboard tab: the stale `moreTab` state was being written as a hash fragment even when the core view was active; fix writes `/` for the core tab
- Bug fix for Knowledge Library tab: the helper was over-delegating to a null return causing the hash to not update on library tab selection; fix writes `/library` explicitly
- Do NOT change the `#/library?...` hash format written by `useLibraryUrlState` — CommandPalette deep-links and shareable entry links depend on it; the router adapts to recognize it instead

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added vitest dev dependency — no test runner existed**
- **Found during:** Task 1 (TDD RED phase)
- **Issue:** Dashboard project had no test runner; `bun test` command not configured; could not run TDD
- **Fix:** Added vitest@4.1.7 as dev dependency and configured it in package.json scripts
- **Files modified:** dashboard/package.json
- **Verification:** 30/30 vitest tests pass
- **Committed in:** efeb471 (Task 1 RED commit)

**2. [Rule 2 - Scope Extension, User-Approved] Added tabStateToRoute write-side inverse**
- **Found during:** Task 3 checkpoint review with user
- **Issue:** Original plan only fixed read-side (deep-link/refresh); in-app tab switches did not update the URL, making it impossible to bookmark or share current tab state after navigation
- **Fix:** Added `tabStateToRoute` inverse helper (Task 3b) and wired it into DashboardPage tab-change handlers so every in-app tab switch pushes a matching hash
- **Files modified:** dashboard/src/lib/dashboardRoutes.ts, dashboard/src/lib/dashboardRoutes.test.ts, dashboard/src/components/dashboard/DashboardPage.tsx
- **Verification:** Human-verified all tabs update URL correctly in-app
- **Committed in:** 590fe03 (RED), 85e6c47 (GREEN), 8902ccf (wiring)

**3. [Rule 1 - Bug] Fixed Core Dashboard and Knowledge Library tab URL hash writing**
- **Found during:** Task 3b wiring
- **Issue:** tabStateToRoute for Core Dashboard tab was writing the stale `moreTab` hash (e.g. `#/graph`) when switching back to core; Knowledge Library tab hash was not being written (null return path)
- **Fix:** Explicit branch for core view writes `#/`, explicit branch for library writes `#/library`
- **Files modified:** dashboard/src/components/dashboard/DashboardPage.tsx
- **Verification:** Human-verified Core and Library tab URL writes in-app
- **Committed in:** da39e58 (bug fix commit)

---

**Total deviations:** 3 (1 blocking dependency fix, 1 user-approved scope extension, 1 bug fix)
**Impact on plan:** All deviations necessary. vitest was essential for TDD. Scope extension was explicitly approved. Bug fix corrected incorrect hash writes discovered during wiring.

## Issues Encountered

- In-app routing worked fine during live navigation (replaceState does not fire hashchange), so the UAT item 8 bug was only reproducible on hard refresh/new-tab deep-link — required a careful distinction between in-app nav and URL-direct access when diagnosing the root cause

## Open / Deferred Items

**UAT items 9–13 — deferred to post-deploy human testing**

These items require the backend running locally with actual indexed library entries. The local environment during testing had no data present. Since item 8 is fixed and the routing is correct, items 9–13 are expected to pass once data is present. They are NOT this plan's must_haves.

| Item | Description | Status |
|------|-------------|--------|
| 9 | Library page renders filters, view switcher, entry grid | Deferred — no local data |
| 10 | Search returns matching entries | Deferred — no local data |
| 11 | Card/Compact/Table view switcher renders entries | Deferred — no local data |
| 12 | Q&A panel returns grounded answer | Deferred — no local data |
| 13 | Pagination and sort controls update the entry list | Deferred — no local data |

The orchestrator will track these as a HUMAN-UAT file for post-deploy verification.

## Next Phase Readiness

- Dashboard hash routing is now correct and self-consistent — all dashboard tabs are bookmarkable and deep-linkable
- The `dashboardRoutes.ts` module is the extension point for any future dashboard tabs; just add the segment to the mapping there
- UAT items 9–13 ready for post-deploy human testing with real backend data
- No blockers for Phase 3 continued execution or Phase 4

## Threat Surface Scan

No new security-relevant surface introduced. `routeToTabState` is a total function over arbitrary strings (segment compared against a fixed allow-list, never used to construct DOM or URLs, unknown segments return null → NotFound). No new network endpoints, auth paths, or schema changes. Consistent with the plan's T-03-01 disposition.

## Self-Check: PASSED

- `dashboard/src/lib/dashboardRoutes.ts` — confirmed exists (committed `19c0097`)
- `dashboard/src/lib/dashboardRoutes.test.ts` — confirmed exists (committed `efeb471`)
- `dashboard/src/App.tsx` — modified in `1477c3d`
- `dashboard/src/components/dashboard/DashboardPage.tsx` — modified in `66e987b`, `8902ccf`, `da39e58`
- dashboard branch pushed: `git push` succeeded, remote ref set
- Parent repo SHA bumped: `e661794` — `git submodule status` shows `da39e58` with no `+`/`-` prefix
- 30/30 vitest tests pass (human-verified before checkpoint)
- `bun run build` clean (human-verified before checkpoint)

---
*Phase: 03-knowledge-library*
*Completed: 2026-05-30*
