---
status: partial
phase: 05-onboarding-instant-win
source: [05-VERIFICATION.md]
started: 2026-05-31T04:15:00Z
updated: 2026-05-31T04:15:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Visual check of honest labeling on cold-start digest card
expected: On cold start (no OAuth), the InstantWinDigest card shows "Preview" / "What Signal will do for you" — NOT "Your first digest" / "Last 24 hours"
result: [pending]

### 2. Runtime test of LLM failure graceful degradation
expected: When LLM returns 502, IdentityBox stays on Step 1 and shows an error message — does NOT advance wizard with null profile, does NOT get stuck on "Analyzing..."
result: [pending]

### 3. Panel B (AI Guide) visibility during all onboarding steps
expected: AI Guide panel is visible and provides contextual guidance during all wizard steps
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
