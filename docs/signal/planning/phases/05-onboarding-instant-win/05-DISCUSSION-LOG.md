# Phase 5: Onboarding + Instant Win - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-31
**Phase:** 5-onboarding-instant-win
**Areas discussed:** Identity Box & Profile, Onboarding Flow & Steps, First-Run Detection & Re-entry, Instant Win Digest

---

## Identity Box & Profile

| Option | Description | Selected |
|--------|-------------|----------|
| Single free-text box | One text box: 'Tell me what you do and what overwhelms you.' Fastest path. | |
| Guided prompt sequence | 2-3 short prompts. Guided but slower. Each answer feeds profile incrementally. | |
| Single box with placeholder examples | Single box with rotating example text. Hints without constraining. | |

**User's choice:** Guided prompt sequence (but refined to 1 prompt + AI follow-up)
**Notes:** User wants conversational flow — not a multi-field form. AI asks follow-up if needed.

| Option | Description | Selected |
|--------|-------------|----------|
| Structured JSON + summary card | AI parses into structured JSON (role, pain_points, apps, templates). Guide shows summary card. | ✓ |
| Context templates only | AI generates templates directly. Simpler but harder to evolve. | |
| Natural-language summary | AI produces a paragraph. Human-readable, no schema. | |

**User's choice:** Structured JSON + summary card
**Notes:** Structured data is more evolvable. Summary card makes it human-reviewable.

| Option | Description | Selected |
|--------|-------------|----------|
| Confirmation card in Panel A | Card with bullets: 'Here's what I understood.' Owner can edit or confirm. | ✓ |
| Guide chat message | Guide in Panel B speaks the profile. Owner replies to confirm/edit. | |
| Full-screen overlay | Full-screen with edit buttons per field. More formal. | |

**User's choice:** Confirmation card in Panel A
**Notes:** Consistent with Panel A being the content area. Panel B (Guide) stays locked.

| Option | Description | Selected |
|--------|-------------|----------|
| 2 prompts | Role → Pain points. Fast, covers basics. Apps inferred. | |
| 3 prompts | Role → Pain points → Apps. More explicit but adds a step. | |
| 1 prompt + AI follow-up | One prompt, AI asks follow-up if needed. Most conversational. | ✓ |

**User's choice:** 1 prompt + AI follow-up
**Notes:** Conversational and adaptive. Matches the AI Guide personality.

---

## Onboarding Flow & Steps

| Option | Description | Selected |
|--------|-------------|----------|
| 3-step linear wizard | Identity → Confirmation + Connect → Digest. 3 screens, linear, PRD-aligned. | ✓ |
| Single scrollable screen | All on one scrollable Panel A. Progressive disclosure. | |
| Conversational (Guide-led) | Guide takes over conversationally. No separate screens. | |

**User's choice:** 3-step linear wizard
**Notes:** Clear, predictable, matches the < 2 min target.

| Option | Description | Selected |
|--------|-------------|----------|
| Show relevant apps only | 2-3 most relevant apps based on profile. Connect button each. Skip rest. | ✓ |
| All apps, highlight relevant | All supported apps, relevant ones highlighted. More choice, more cognitive load. | |
| Auto-connect top app | Auto-connect most relevant app immediately. Fastest but surprising. | |

**User's choice:** Show relevant apps only
**Notes:** Focused. Owner can add more later from settings.

| Option | Description | Selected |
|--------|-------------|----------|
| Allow skip | 'Skip for now' link. Digest works with whatever's available. | ✓ |
| Require at least one | Must connect at least one app. Digest needs real data. | |
| No skip, placeholder digest | Just 'Next' button. No data = placeholder. | |

**User's choice:** Allow skip
**Notes:** Respects the < 2 min target. OAuth flows can be slow.

| Option | Description | Selected |
|--------|-------------|----------|
| Step indicator | 'Step 1 of 3' or dots at top of Panel A. Subtle. | ✓ |
| Guide announces steps | Guide in Panel B announces each step. Implicit progress. | |
| No progress indicator | Each step flows naturally. Minimal but disorienting. | |

**User's choice:** Step indicator
**Notes:** Keeps owner oriented without being heavy-handed.

---

## First-Run Detection & Re-entry

| Option | Description | Selected |
|--------|-------------|----------|
| Backend profile check | No profile → onboarding. Profile exists → Zen shell. No localStorage. | ✓ |
| localStorage flag + backend fallback | localStorage for instant UI decision. Backend fallback if flag missing. | |
| Dual check | Both localStorage and backend. Most robust but two sources of truth. | |

**User's choice:** Backend profile check
**Notes:** Single source of truth. No localStorage sync issues.

| Option | Description | Selected |
|--------|-------------|----------|
| Skip to Zen shell | Go straight to Core Dashboard. Onboarding is one-time. | ✓ |
| Welcome back overlay | Brief overlay with yesterday's digest. Dismissible. | |
| Zen shell + profile nudge | Zen shell with subtle 'Update your profile' in Guide. | |

**User's choice:** Skip to Zen shell
**Notes:** Onboarding is a one-time experience. Re-onboard via Panic Button (Phase 9).

| Option | Description | Selected |
|--------|-------------|----------|
| Resume from last step | Save progress after each step. Resume on return. | ✓ |
| Start over | Onboarding is fast, redoing isn't painful. Simpler. | |
| Skip completed steps | If profile exists, skip to step 2. Partial progress. | |

**User's choice:** Resume from last step
**Notes:** Backend tracks which step is completed. Graceful interruption handling.

| Option | Description | Selected |
|--------|-------------|----------|
| Guide chat only for now | Profile set once. Changes via Guide chat. No settings page. | ✓ |
| Edit button on confirmation card | Re-open Identity Box before confirming. After, Guide chat only. | |
| Settings page | Dedicated editable profile fields. More discoverable. | |

**User's choice:** Guide chat only for now
**Notes:** Settings page is a future phase. Guide chat is sufficient for now.

---

## Instant Win Digest

| Option | Description | Selected |
|--------|-------------|----------|
| Context Nest card | Same pattern as Phase 4 stream cards. 3 bullets, last 24 hours. | ✓ |
| Full-screen overlay | Ceremonial modal with richer layout. Blocks the shell. | |
| Dedicated Clarity Board view | Persistent view in Clarity Board. More work, more useful long-term. | |

**User's choice:** Context Nest card
**Notes:** Consistent with Zen shell patterns. Reuses existing card component.

| Option | Description | Selected |
|--------|-------------|----------|
| Capability preview | 'Here's what I'll do for you' with example bullets from profile. | ✓ |
| Demo data digest | Sample data to show what a real digest looks like. Impressive but misleading. | |
| Skip if no data | 'Come back tomorrow' message. Honest but anticlimactic. | |

**User's choice:** Capability preview
**Notes:** Honest about what's available. Sets expectations without faking data.

| Option | Description | Selected |
|--------|-------------|----------|
| Connected sources only | Gmail, YouTube, library, news — whatever's connected. No data = preview. | ✓ |
| Connected + public news | Always has at least one data point. Adds dependency. | |
| All available brain data | Connected + library + planning. Most comprehensive. | |

**User's choice:** Connected sources only
**Notes:** No hidden dependencies. What you connect is what you get.

| Option | Description | Selected |
|--------|-------------|----------|
| Guide message + transition | 'You're all set' + Get started button → Zen shell. | ✓ |
| Auto-transition with timer | 5-second timer with Skip button. Smooth but rushed. | |
| No explicit completion | Digest card stays. Owner starts using naturally. | |

**User's choice:** Guide message + transition
**Notes:** Clear conclusion moment. Natural transition to normal usage.

---

## Claude's Discretion

- Exact Identity Box placeholder text and AI follow-up prompt wording
- Profile JSON schema field names and structure
- Step indicator animation style
- Context Nest card styling for the digest (reuse Phase 4 card pattern)
- OAuth flow error handling during app connect step
- Capability preview content generation from profile data

## Deferred Ideas

None — discussion stayed within phase scope
