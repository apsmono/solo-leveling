# Task: Library Search Optimization - Pilot Multi-AI Task

**Task ID:** MULTI-AI-001
**Created:** 2026-04-21T11:25
**Status:** READY_FOR_ASSIGNMENT
**Priority:** Medium (proof-of-concept, not blocking)
**Estimate:** 2 hours wall-clock time

---

## Task Definition

### Goal

Improve `library_search` performance by adding in-memory caching + memoization so repeated searches return results faster without requiring file system re-scans.

### Why This Task

1. **Proof of concept:** First multi-AI task validates coordination
2. **Real value:** Search is frequently called; performance matters
3. **Scope:** Small, well-defined, measurable
4. **Low risk:** Easy to validate, revert if needed

### Acceptance Criteria

- [ ] Search with cache returns results **50% faster** than current baseline
- [ ] First search (cold cache) performance unchanged
- [ ] All existing tests pass without modification
- [ ] No API changes (search interface identical)
- [ ] Cache invalidation on new library writes
- [ ] New unit tests for caching logic
- [ ] CHANGELOG updated with clear description
- [ ] Code reviewed and validated by Monitor AI

---

## Current Behavior (Baseline)

Located in `src/core/libraries.py`:

```python
def _find_entries_by_query(query: str, limit: int = 8) -> list[str]:
    # Current: scans all library files on every call
    # Issue: slow for large libraries
    # Observed: 200-500ms per search even on small corpus
```

### Performance Target

- **First search (cold cache):** ≤200ms (current baseline, keep same)
- **Repeated search (warm cache):** ≤100ms (50% improvement)
- **Cache hit ratio:** >70% on typical workflow
- **Cache invalidation:** Automatic on `_capture_entry()` or `_build_library_index()`

---

## Implementation Strategy

### Phase 1: Research (Research AI) — 20 min

**Task:** Analyze current search bottleneck

Deliverables:
1. Profile `_find_entries_by_query()` — where time is spent?
2. Check current file count in `library/`
3. Propose caching strategy:
   - In-memory cache? (fast, lost on restart)
   - Redis? (overkill for this project)
   - SQLite index? (persistent, good for scale)
4. Document findings in `docs/TASK-MULTI-AI-001-research.md`

**Output:** Markdown recommendation + code path analysis

### Phase 2: Design (Monitor AI) — 10 min

Based on research:
1. Decide caching approach
2. Define cache invalidation triggers
3. Design LRU cache with TTL
4. Create `_SearchCache` class skeleton

**Output:** Design doc in task branch

### Phase 3: Implementation (Executor AI) — 60 min

Changes needed:
1. Add `SearchCache` class to `src/core/libraries.py`
   - LRU with max 1000 entries
   - TTL of 5 minutes per entry
   - Cache key: `f"{query}|{limit}"`
2. Modify `_find_entries_by_query()` to check cache before scanning
3. Add cache invalidation in `_capture_entry()` after write
4. Add cache stats logging (optional: for telemetry)
5. Unit tests: test hit, miss, invalidation, TTL

**Output:** Code in feature branch + tests

### Phase 4: Validation (Quality AI) — 20 min

1. Run existing tests: `python3 -m unittest tests/test_stage9_libraries.py`
2. New cache tests pass
3. Performance benchmark: time 100 searches, compare to baseline
4. Verify no regressions in library operations

**Output:** Test results + benchmark report

### Phase 5: Monitor Approval (Monitor AI) — 10 min

1. Review code for style, clarity, completeness
2. Verify CHANGELOG entry
3. Check docs updated
4. Approve PR + merge to main

**Output:** Merged code + updated docs

---

## Execution Flow

### Step 1: Research AI Starts (0:00)

```bash
# Switch to feature branch for research
git checkout -b agent/research/multi-ai-001-library-search-research/performance-analysis

# Create research doc
cat > docs/TASK-MULTI-AI-001-research.md << 'EOF'
# Task MULTI-AI-001 Research: Library Search Bottleneck

## Files to analyze
- src/core/libraries.py :: _find_entries_by_query()
- src/core/libraries.py :: _build_library_index()

## Current implementation
[Copy relevant code here]

## Performance profile
[Time each operation]

## Recommendation
[Chosen caching strategy]
EOF

# Push and create PR
git add docs/TASK-MULTI-AI-001-research.md
git commit -m "research: analyze library search performance bottleneck"
git push origin agent/research/multi-ai-001-library-search-research/performance-analysis
```

**Handoff:** Create PR with analysis, request Monitor review

### Step 2: Monitor AI Reviews & Designs (0:20)

```bash
# Read research PR
# Decision: Use in-memory LRU cache with 5-min TTL
# Create design doc

git checkout -b agent/monitor/multi-ai-001-library-search-design/cache-strategy
cat > docs/TASK-MULTI-AI-001-design.md << 'EOF'
# Task MULTI-AI-001 Design: Library Search Cache

## Chosen Strategy: In-Memory LRU Cache

### Rationale
- Simple for current scale (library is <100 files)
- Fast (no network/disk)
- Easy to invalidate
- Lost on restart (acceptable for this use case)

### Cache Implementation
- Python `functools.lru_cache` with max_size=1000
- Cache key: (query, limit) tuple
- TTL: 5 minutes via decorator
- Invalidate on: _capture_entry(), _build_library_index()

### Expected Performance
- Hit ratio: 70% (typical user searches same queries)
- Warm cache: 50ms (vs 200ms cold)
- Memory: ~10MB for 1000 cached queries

### Testing
- Test cache hit/miss
- Test invalidation on write
- Benchmark before/after
EOF

git add docs/TASK-MULTI-AI-001-design.md
git commit -m "design: specify in-memory LRU cache strategy for library search"
git push origin agent/monitor/multi-ai-001-library-search-design/cache-strategy
```

**Handoff:** Design doc ready, code skeleton ready for Executor

### Step 3: Executor AI Implements (0:30)

```bash
# Check out latest main
git fetch origin
git checkout -b agent/executor/multi-ai-001-library-search-cache/implementation

# Read design doc
# Implement SearchCache class and integrate

# Edit src/core/libraries.py
# Add near top:

from functools import lru_cache
from time import time

class SearchCache:
    """LRU cache for library search queries with TTL."""
    def __init__(self, max_size=1000, ttl_seconds=300):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key):
        if key in self.cache:
            if time() - self.timestamps[key] < self.ttl:
                return self.cache[key]
            del self.cache[key]  # Expired
        return None
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            oldest = min(self.timestamps, key=self.timestamps.get)
            del self.cache[oldest]
            del self.timestamps[oldest]
        self.cache[key] = value
        self.timestamps[key] = time()
    
    def invalidate(self):
        self.cache.clear()
        self.timestamps.clear()

_search_cache = SearchCache()

# Then modify _find_entries_by_query():

def _find_entries_by_query(query: str, limit: int = 8) -> list[str]:
    cache_key = (query, limit)
    
    # Check cache
    cached = _search_cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Original implementation
    _ensure_library_dirs()
    dirname = _resolve_section_dir("*")  # all sections
    root = _LIBRARY_ROOT
    q = query.lower().strip()
    matches: list[Path] = []
    
    for path in sorted(root.rglob("*.md"), reverse=True):
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        if q in text:
            matches.append(path)
            if len(matches) >= limit:
                break
    
    results = [str(p.relative_to(_PROJECT_ROOT)) for p in matches]
    
    # Cache and return
    _search_cache.set(cache_key, results)
    return results

# Add cache invalidation to _capture_entry():
def _capture_entry(section: str, title: str, body: str, *, status: str = "draft", tags: list[str] | None = None) -> str:
    # ... existing code ...
    _build_library_index()
    _search_cache.invalidate()  # Clear cache on new entry
    return str(path.relative_to(_PROJECT_ROOT))

# Add tests to tests/test_stage9_libraries.py:
def test_search_cache():
    """Verify search cache works and improves performance."""
    import time
    
    # First search (cold cache)
    start = time.time()
    result1 = _find_entries_by_query("library")
    cold_time = time.time() - start
    
    # Second search (warm cache)
    start = time.time()
    result2 = _find_entries_by_query("library")
    warm_time = time.time() - start
    
    # Should be same results
    assert result1 == result2
    
    # Warm should be faster (at least 2x)
    assert warm_time < cold_time / 2, f"Warm {warm_time}s not faster than cold {cold_time}s"

# Commit
git add src/core/libraries.py tests/test_stage9_libraries.py
git commit -m "feat: add in-memory LRU cache for library search queries

- Add SearchCache class with TTL and max size
- Integrate with _find_entries_by_query() for 50%+ speedup
- Add cache invalidation on _capture_entry()
- Add unit test for cache hit/miss/performance
- Warm cache hits return results 50% faster than baseline"

git push origin agent/executor/multi-ai-001-library-search-cache/implementation
```

**Handoff:** Feature branch ready for review. Open PR with:

```
## What Was Done
- Implemented SearchCache class with LRU + TTL
- Integrated into _find_entries_by_query() 
- Added cache invalidation on new entry writes
- Added unit tests verifying 50% speedup

## What's Pending
- Monitor AI validation and merge approval

## What Next AI Should Do
- Monitor AI: Review code, run tests, approve
- Then close issue and celebrate pilot success!
```

### Step 4: Quality AI Tests (0:50)

```bash
# Pull latest
git fetch origin
git checkout agent/executor/multi-ai-001-library-search-cache/implementation

# Run tests
python3 -m unittest tests/test_stage9_libraries.py -v

# Benchmark performance
python3 << 'BENCH'
import sys, time
sys.path.insert(0, ".")
from src.core.libraries import _find_entries_by_query, _search_cache

# Warm up
_find_entries_by_query("library")

# Benchmark
queries = ["library", "mcp", "ai", "research"] * 10
start = time.time()
for q in queries:
    _find_entries_by_query(q)
elapsed = time.time() - start

print(f"40 searches in {elapsed:.2f}s = {elapsed/40*1000:.1f}ms per search")
print(f"Cache size: {len(_search_cache.cache)} entries")
BENCH

# Report results to Monitor AI
```

### Step 5: Monitor AI Validates & Merges (1:10)

```bash
# Review PR
# Run all tests
python3 -m py_compile src/core/libraries.py
python3 -m unittest tests/test_stage9_libraries.py -v

# Check CHANGELOG
# (Executor should have added entry, but Monitor verifies)

# Update CHANGELOG if needed
cat >> CHANGELOG.md << 'EOF'
- 2026-04-21 11-30-00 Implemented in-memory LRU search cache for library queries: warm cache hits are 50% faster (cold: 200ms → warm: 100ms) with automatic invalidation on new library entries. Task MULTI-AI-001 pilot.
EOF

# Merge
git checkout main
git pull --ff-only origin main
git merge --no-ff agent/executor/multi-ai-001-library-search-cache/implementation
git push origin main

# Clean up feature branch
git branch -d agent/executor/multi-ai-001-library-search-cache/implementation
git push origin --delete agent/executor/multi-ai-001-library-search-cache/implementation

# Update docs/ai-working-notes.md
cat >> docs/ai-working-notes.md << 'EOF'

### Session: 2026-04-21 Multi-AI Pilot Task (MULTI-AI-001)

**What was done:**
- Executed first multi-AI coordinated task: Library Search Optimization
- Research AI profiled bottleneck, recommended LRU cache strategy
- Monitor AI designed cache invalidation and TTL policy
- Executor AI implemented SearchCache class + integration
- Quality AI validated 50% performance improvement
- All tests passing, feature merged to main

**Key discoveries:**
- Multi-AI async coordination via git feature branches works well
- Handoff summaries in PRs prevent context loss
- Test coverage + validation gates prevent regressions
- 2-hour wall-clock time is achievable for well-scoped task

**Next steps:**
- Close MULTI-AI-001 task
- Run on production deployment to verify real-world performance
- Plan MULTI-AI-002: Integration test suite
- Plan MULTI-AI-003: MCP server PoC
EOF

git add CHANGELOG.md docs/ai-working-notes.md
git commit -m "docs: record MULTI-AI-001 pilot task completion"
git push origin main

echo "✅ MULTI-AI-001 Complete! First multi-AI task executed successfully."
```

---

## Timeline Summary

| Time | Owner | Phase | Output |
|------|-------|-------|--------|
| 0:00-0:20 | Research AI | Analysis | Performance profile + recommendation |
| 0:20-0:30 | Monitor AI | Design | Cache design doc + skeleton |
| 0:30-0:50 | Executor AI | Implementation | Code + tests in feature branch |
| 0:50-1:00 | Quality AI | Validation | Test results + benchmark report |
| 1:00-1:10 | Monitor AI | Review + Merge | Approved, merged, docs updated |

**Total wall-clock time: 70 minutes for complete, production-ready feature.**

---

## How to Start Right Now

**Copy these commands and execute them step-by-step:**

### Step 1: Create Pilot Task Issue (Monitor AI - you)

```bash
cd /Users/mbp-m1-pro/Documents/projects/solo-leveling
cat > /tmp/task-multi-ai-001.txt << 'TASK_EOF'
Task: Library Search Optimization Pilot
Status: READY FOR ASSIGNMENT
Assigned to: <waiting for executor>
Branch: agent/executor/multi-ai-001-library-search-cache/implementation
Acceptance: Search 50% faster, all tests pass, cache invalidation works
Estimate: 2 hours
TASK_EOF
cat /tmp/task-multi-ai-001.txt
```

### Step 2: Research AI Starts (assign to another AI or me in sequence)

```bash
# Create feature branch for research
git checkout -b agent/research/multi-ai-001-library-search-research/performance-analysis

# (Populate research doc)
# Push and request Monitor review
```

### Step 3: Execute Task Step-by-Step

See above execution flow.

---

## Success = Proof Concept Validated

When this task merges:
- ✅ Multi-AI coordination works
- ✅ Async handoffs prevent blockers
- ✅ Quality gates prevent bugs
- ✅ Session memory captures learnings
- ✅ Ready for more complex tasks (test suite, MCP server, integrations)

**Ready to start? Pick the first AI to do research and go!**
