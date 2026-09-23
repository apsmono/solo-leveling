# Phase 5: Onboarding + Instant Win - Research

**Researched:** 2026-05-31
**Domain:** Onboarding wizard, AI profile parsing, app connection flow, digest generation
**Confidence:** HIGH

## Summary

Phase 5 delivers the guided sub-2-minute first-run experience. The owner enters free text in an Identity Box, the AI Guide parses it into a structured profile, the system highlights and connects relevant apps, and finishes by generating a first live 24-hour mini-digest. This phase builds on Phase 3's AI Guide panel and Phase 4's Zen shell, rendering the onboarding wizard in Panel A while keeping the Guide panel visible in Panel B.

The implementation spans two repositories: new API endpoints in `solo-leveling/` (profile CRUD, identity parsing, app connection, digest generation) and new React components in `dashboard/` (OnboardingWizard, IdentityBox, ProfileConfirmationCard, AppConnectStep, InstantWinDigest). The backend reuses `run_agent()` for LLM-based profile parsing and follows the existing `require_auth` pattern for all endpoints. The frontend follows the DashboardPage state-lifting pattern established in Phase 3.

**Primary recommendation:** Implement as 3 vertical slices (backend endpoints per wizard step + corresponding frontend component), with the wizard container and routing logic as a shared foundation.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Input format: 1 initial prompt + AI follow-up -- conversational, not a multi-field form
- **D-02:** Profile output: Structured JSON (role, pain_points, connected_apps, context_templates) stored in the brain. Guide shows confirmation card in Panel A
- **D-03:** Profile confirmation card: owner can edit or confirm before proceeding
- **D-04:** Step sequence: 3-step linear wizard rendered in Panel A
- **D-05:** App connect shows only 2-3 most relevant apps based on parsed profile
- **D-06:** App connection is skippable
- **D-07:** Progress indicator: step indicator at top of Panel A
- **D-08:** Detection: backend profile check -- no profile exists -> onboarding
- **D-09:** Return visits: skip straight to Zen shell
- **D-10:** Interruption handling: resume from last completed step
- **D-11:** Profile editing post-onboarding: Guide chat only
- **D-12:** Digest format: Context Nest card pattern, 3 bullets
- **D-13:** Cold-start fallback: capability preview with example bullets
- **D-14:** Data sources: connected sources only
- **D-15:** Completion: Guide says "You're all set" + "Get started" button

### Claude's Discretion
- Exact Identity Box placeholder text and AI follow-up prompt wording
- Profile JSON schema field names and structure
- Step indicator animation style
- Context Nest card styling for the digest (reuse Phase 4 card pattern)
- OAuth flow error handling during app connect step
- Capability preview content generation from profile data

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ONB-02 | Identity Box captures free text; AI Guide parses into working profile / context templates | `run_agent()` in dispatcher.py for LLM parsing; new `/api/v1/onboarding/parse-identity` endpoint; ProfileConfirmationCard component |
| ONB-03 | Guide highlights and connects relevant apps via brain's existing integrations | Existing integration clients (gmail, youtube, etc.) hold OAuth tokens; new `/api/v1/onboarding/connect-app` endpoint triggers OAuth; AppConnectStep component |
| ONB-04 | Generate and display first live 24-hour mini-digest (< 2 min total) | `run_agent()` for digest summarization; `/api/v1/onboarding/digest` endpoint queries connected sources; InstantWinDigest component reuses StreamCard pattern |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Profile parsing (free text -> structured JSON) | API / Backend | — | LLM calls via `run_agent()` live in the brain; frontend sends raw text, receives structured profile |
| Onboarding wizard UI | Browser / Client | — | Pure React state machine in Panel A; no SSR |
| Onboarding step tracking | API / Backend | — | Persisted per-owner so interrupted sessions resume (D-10) |
| App connection (OAuth flow) | API / Backend | Browser / Client | Backend triggers OAuth via existing integration clients; frontend shows connect button and handles redirect |
| Digest generation | API / Backend | — | Queries connected data sources, summarizes via LLM; frontend displays result |
| First-run detection | API / Backend | — | `GET /api/v1/profile` returns 404 if no profile exists (D-08) |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | existing | API endpoints | Already the brain's framework; all new endpoints extend it |
| `run_agent()` (dispatcher.py) | existing | LLM profile parsing + digest generation | Already used for intent parsing, Q&A synthesis; reuse for onboarding |
| React + TypeScript | existing | Frontend components | Dashboard already uses this stack |
| Tailwind CSS v4 | existing | Styling | All components use Tailwind utility classes + CSS custom properties |
| Lucide React | existing | Icons | Already in dashboard; use Mail, Youtube, Rss, Sparkles, CheckCircle |
| Button component | existing | CTA buttons | `dashboard/src/components/ui/Button.tsx` with primary/secondary/ghost variants |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Firebase Auth | existing | OAuth token source | App connection reuses brain's existing integration clients which hold Firebase-managed tokens |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `run_agent()` for profile parsing | Dedicated prompt template module | run_agent() already handles system prompts and structured output; no need for a separate abstraction |
| Backend profile check for first-run detection | localStorage flag | localStorage is per-browser, not per-account; backend check is authoritative (D-08) |
| Separate onboarding API router | Extend guide.py | Separate router keeps concerns clean; onboarding has distinct endpoints from the Guide panel |

## Package Legitimacy Audit

No new external packages are required for this phase. All implementation uses existing dependencies already in `solo-leveling/requirements.txt` and `dashboard/package.json`.

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| (none) | — | — | — | — | — | No new packages needed |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Dashboard (Browser)                                            │
│                                                                 │
│  ┌──────────────────────────────┐  ┌─────────────────────────┐  │
│  │  Panel A (flex-[7])          │  │  Panel B (flex-[3])     │  │
│  │                              │  │                         │  │
│  │  ┌─────────────────────────┐ │  │  AIGuidePanel           │  │
│  │  │  OnboardingWizard       │ │  │  (locked, always        │  │
│  │  │                         │ │  │   visible)              │  │
│  │  │  Step 1: IdentityBox    │ │  │                         │  │
│  │  │    ↓ POST /parse-identity│ │  │  Guide messages during  │  │
│  │  │  Step 2: ProfileConfirm │ │  │  onboarding:            │  │
│  │  │    + AppConnect         │ │  │  - "Analyzing..."       │  │
│  │  │    ↓ POST /connect-app  │ │  │  - AI follow-up prompt  │  │
│  │  │  Step 3: InstantWin     │ │  │  - Completion message   │  │
│  │  │    ↓ GET /digest        │ │  │                         │  │
│  │  │    → "Get started"      │ │  │                         │  │
│  │  └─────────────────────────┘ │  └─────────────────────────┘  │
│  └──────────────────────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
           │                              │
           │ REST API (Firebase Bearer)   │
           ▼                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Brain (solo-leveling FastAPI)                                  │
│                                                                 │
│  /api/v1/profile (GET/POST)         → Profile CRUD              │
│  /api/v1/profile/onboarding-step    → Step progress tracking    │
│  /api/v1/onboarding/parse-identity  → run_agent() profile parse │
│  /api/v1/onboarding/connect-app     → OAuth flow trigger        │
│  /api/v1/onboarding/digest          → Data query + LLM summary  │
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ dispatcher   │  │ integrations │  │ library_store        │   │
│  │ run_agent()  │  │ gmail/youtube│  │ recent entries       │   │
│  └─────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure

```
solo-leveling/src/api/
├── onboarding.py          # NEW: /onboarding/* endpoints
├── profile.py             # NEW: /profile/* endpoints
├── v1_router.py           # EVOLVE: register onboarding + profile routers

solo-leveling/src/core/
├── profile_store.py       # NEW: profile JSON persistence (data/profile.json)
├── onboarding.py          # NEW: profile parsing logic, digest generation

dashboard/src/components/onboarding/
├── OnboardingWizard.tsx   # NEW: top-level wizard container
├── IdentityBox.tsx        # NEW: Step 1 -- free text input
├── ProfileConfirmation.tsx# NEW: Step 2 -- parsed profile card
├── AppConnectStep.tsx     # NEW: Step 2b -- app connection cards
├── InstantWinDigest.tsx   # NEW: Step 3 -- first digest card
├── StepIndicator.tsx      # NEW: progress dots

dashboard/src/hooks/
├── useOnboarding.ts       # NEW: onboarding state management
```

### Pattern 1: OnboardingWizard State Machine

**What:** A 3-step linear wizard that replaces ClarityBoard content in Panel A during onboarding.

**When to use:** When the owner has no profile (first-run detection via `GET /api/v1/profile` returning 404).

**Example:**
```typescript
// Source: DashboardPage.tsx pattern (state lifting) + UI-SPEC
type OnboardingStep = 1 | 2 | 3;
type OnboardingState = "loading" | "onboarding" | "complete";

// In DashboardPage:
const [onboardingState, setOnboardingState] = useState<OnboardingState>("loading");
const [onboardingStep, setOnboardingStep] = useState<OnboardingStep>(1);
const [profile, setProfile] = useState<ProfileData | null>(null);

// First-run detection on mount
useEffect(() => {
  apiGet("/api/v1/profile")
    .then(() => setOnboardingState("complete"))
    .catch((err) => {
      if (err.message?.includes("404")) setOnboardingState("onboarding");
      else setOnboardingState("complete"); // network error -> skip onboarding
    });
}, []);

// Panel A conditional render
const panelA = onboardingState === "onboarding" ? (
  <OnboardingWizard
    step={onboardingStep}
    profile={profile}
    onStepChange={setOnboardingStep}
    onComplete={() => setOnboardingState("complete")}
    onProfileParsed={setProfile}
  />
) : (
  <ClarityBoard ... />
);
```

### Pattern 2: LLM Profile Parsing via run_agent()

**What:** Send free text to the brain, get structured JSON profile back.

**When to use:** Step 1 of onboarding when the owner submits their Identity Box text.

**Example:**
```python
# Source: intent_parser.py pattern + dispatcher.py run_agent()
PROFILE_SYSTEM_PROMPT = """You are a profile parser for a personal command center.
Given the owner's description of their work and pain points, extract a structured profile.

Respond with valid JSON only. No markdown, no explanations.

Format:
{
  "role": "short description of what they do",
  "pain_points": ["pain point 1", "pain point 2"],
  "suggested_apps": ["gmail", "youtube"],
  "context_templates": ["template description 1"],
  "needs_followup": false,
  "followup_question": ""
}

Rules:
- suggested_apps must be from: gmail, youtube, notion, gdrive, github, telegram, discord
- needs_followup: true if the input is too vague to determine apps (e.g., "I work in tech")
- followup_question: a natural follow-up if needs_followup is true
- Keep role to one sentence
- Max 3 pain points, max 3 suggested_apps
"""
```

### Pattern 3: Profile Persistence (local-first)

**What:** Store profile JSON in `data/profile.json` following the brain's local-first pattern.

**When to use:** POST /api/v1/profile saves parsed profile; GET reads it for first-run detection.

**Example:**
```python
# Source: data/n8n_executions.json, data/reminders.json patterns
from pathlib import Path
import json

_PROFILE_PATH = Path("data/profile.json")

def load_profile() -> dict | None:
    if not _PROFILE_PATH.exists():
        return None
    return json.loads(_PROFILE_PATH.read_text())

def save_profile(profile: dict) -> None:
    _PROFILE_PATH.write_text(json.dumps(profile, indent=2))

def load_onboarding_step() -> int:
    profile = load_profile()
    if not profile:
        return 1
    return profile.get("onboarding_step", 1)

def save_onboarding_step(step: int) -> None:
    profile = load_profile() or {}
    profile["onboarding_step"] = step
    save_profile(profile)
```

### Anti-Patterns to Avoid

- **localStorage for first-run detection:** Per-browser, not per-account. Use backend profile check (D-08).
- **Multi-field form for Identity Box:** Locked decision is 1 prompt + AI follow-up (D-01). Do not build a form with separate fields for role, pain points, etc.
- **Showing all supported apps:** Only show 2-3 most relevant based on profile (D-05). Do not enumerate every integration.
- **Blocking onboarding if app connection fails:** App connect is skippable (D-06). Digest works with whatever data is available.
- **Replacing Panel B during onboarding:** AIGuidePanel stays locked and visible. Onboarding only swaps Panel A content.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Profile parsing from free text | Custom NLP/regex parser | `run_agent()` with structured JSON prompt | LLM handles edge cases, natural language variety; same pattern as intent_parser.py |
| OAuth flow for app connection | Custom OAuth implementation | Brain's existing integration clients (gmail, youtube, etc.) | Already handle token refresh, credential management; Phase 2 syncs to n8n |
| Digest summarization | Custom summarization logic | `run_agent()` with digest prompt | LLM compresses arbitrary content into 3 bullets consistently |
| Step indicator dots | Custom SVG/canvas | Tailwind divs with conditional classes | Simple dot indicator is pure CSS; no library needed |
| API client functions | Custom fetch wrappers | `apiGet()`, `apiPost()` from `dashboard/src/lib/api.ts` | Already handles auth headers, error handling |

## Common Pitfalls

### Pitfall 1: Profile Parse Latency
**What goes wrong:** LLM call for profile parsing takes 2-5 seconds, making the UI feel frozen.
**Why it happens:** Gemini API latency for structured output.
**How to avoid:** Show a loading state ("Analyzing...") with the existing spinner pattern. The UI-SPEC defines this: loading label "Analyzing..." on the submit button.
**Warning signs:** Button shows spinner but no visual feedback otherwise.

### Pitfall 2: OAuth Redirect Breaks Wizard State
**What goes wrong:** Clicking "Connect" for Gmail redirects the browser to Google OAuth, losing the wizard state.
**Why it happens:** OAuth flows typically redirect the full page.
**How to avoid:** Use popup-based OAuth (same pattern as Phase 1's `signInWithGoogle`). The wizard state persists in the parent window. Alternatively, save onboarding step to backend before redirect (D-10) and resume on return.
**Warning signs:** After OAuth callback, onboarding restarts from Step 1.

### Pitfall 3: Digest Returns Empty on Cold Start
**What goes wrong:** No connected apps means no data to summarize, digest card is empty.
**Why it happens:** All data sources are disconnected.
**How to avoid:** Implement cold-start fallback (D-13): generate capability preview bullets from the profile. "Here's what I'll do for you" with example bullets based on their role and pain points.
**Warning signs:** Digest card shows "No data available" instead of useful content.

### Pitfall 4: Onboarding State Inconsistency
**What goes wrong:** Frontend thinks onboarding is complete but backend has no profile, or vice versa.
**Why it happens:** Network error during profile save, or race condition between state check and render.
**How to avoid:** Backend is the source of truth (D-08). Frontend checks `GET /api/v1/profile` on mount. If 404, show onboarding. If profile exists, skip to Zen shell. Never rely on frontend-only state for this decision.
**Warning signs:** User sees onboarding on one device but Zen shell on another.

### Pitfall 5: AI Follow-up Loop
**What goes wrong:** AI keeps asking follow-up questions, never producing a profile.
**Why it happens:** Prompt doesn't bound the follow-up to a single round.
**How to avoid:** D-01 specifies "1 initial prompt + AI follow-up" -- the system prompt must enforce `needs_followup: true` only once. After the follow-up response, always parse to profile regardless of content quality.
**Warning signs:** User types 3+ responses and wizard stays on Step 1.

## Code Examples

### Verified patterns from existing codebase:

### API Endpoint Pattern (require_auth)
```python
# Source: solo-leveling/src/api/guide.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.deps import require_auth

router = APIRouter()

@router.post("/onboarding/parse-identity")
async def parse_identity(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'text' in request payload.",
        )
    # ... parse via run_agent() ...
    return {"status": "ok", "profile": parsed_profile}
```

### Frontend API Call Pattern
```typescript
// Source: dashboard/src/lib/api.ts
export async function parseIdentity(text: string): Promise<{ status: string; profile: ProfileData }> {
  return apiPost<{ status: string; profile: ProfileData }>("/api/v1/onboarding/parse-identity", { text });
}
```

### StreamCard Pattern (reuse for digest)
```tsx
// Source: dashboard/src/components/zen/StreamCard.tsx
<article className="flex max-h-[140px] flex-col rounded-lg border bg-card p-3 shadow-sm">
  <div className="mb-2 flex items-center justify-between text-xs text-muted">
    <span className="inline-flex items-center gap-1.5 font-medium">
      <Sparkles size={14} className="text-accent" />
      Your first digest
    </span>
    <span>Last 24 hours</span>
  </div>
  <ul className="mb-2 flex-1 space-y-0.5 overflow-hidden text-sm text-text">
    {bullets.map((bullet, i) => (
      <li key={i} className="truncate">• {bullet}</li>
    ))}
  </ul>
</article>
```

### State Lifting Pattern (DashboardPage)
```typescript
// Source: dashboard/src/components/dashboard/DashboardPage.tsx
// Guide chat state is lifted to DashboardPage level so it persists across tab switches.
// Onboarding state follows the same pattern:
const [onboardingState, setOnboardingState] = useState<OnboardingState>("loading");
const [onboardingStep, setOnboardingStep] = useState<OnboardingStep>(1);
const [profile, setProfile] = useState<ProfileData | null>(null);
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Keyword-based intent parsing | LLM structured output via run_agent() | Phase 3 | Profile parsing reuses the same LLM pattern |
| Tab-based navigation | Zen shell 70/30 with ClarityBoard views | Phase 4 | Onboarding renders in Panel A, not a separate page |
| localStorage session state | Backend profile check | Phase 1 | First-run detection is authoritative per-account |

**Deprecated/outdated:**
- INTENT_MAP keyword matching: replaced by LLM intent_parser.py in Phase 3
- Separate page routing: replaced by Zen shell view switching in Phase 4

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` (backend) + none detected (frontend) |
| Config file | none -- tests run via `python -m unittest` |
| Quick run command | `cd solo-leveling && python -m unittest tests.test_onboarding -v` |
| Full suite command | `cd solo-leveling && python -m unittest discover tests -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ONB-02 | Parse free text into structured profile | unit | `python -m unittest tests.test_onboarding -v` | Wave 0 |
| ONB-02 | AI follow-up when input is vague | unit | `python -m unittest tests.test_onboarding -v` | Wave 0 |
| ONB-03 | Profile suggests relevant apps | unit | `python -m unittest tests.test_onboarding -v` | Wave 0 |
| ONB-03 | Connect app triggers OAuth flow | integration | `python -m unittest tests.test_onboarding -v` | Wave 0 |
| ONB-04 | Digest returns 3 bullets from connected data | unit | `python -m unittest tests.test_onboarding -v` | Wave 0 |
| ONB-04 | Cold-start fallback returns capability preview | unit | `python -m unittest tests.test_onboarding -v` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd solo-leveling && python -m unittest tests.test_onboarding -v`
- **Per wave merge:** `cd solo-leveling && python -m unittest discover tests -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `solo-leveling/tests/test_onboarding.py` -- covers ONB-02, ONB-03, ONB-04
- [ ] `solo-leveling/src/core/profile_store.py` -- profile persistence module
- [ ] `solo-leveling/src/api/onboarding.py` -- onboarding endpoints
- [ ] `solo-leveling/src/api/profile.py` -- profile CRUD endpoints
- [ ] `dashboard/src/components/onboarding/` -- all wizard components
- [ ] `dashboard/src/hooks/useOnboarding.ts` -- onboarding state hook
- [ ] Frontend API functions in `dashboard/src/lib/api.ts` for onboarding endpoints

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Firebase Google OAuth via `require_auth` dependency -- all onboarding endpoints require auth |
| V3 Session Management | no | Onboarding is a one-time flow within an authenticated session |
| V4 Access Control | yes | Single-owner model; `SIGNAL_OWNER_ID` scopes all data; profile is per-owner |
| V5 Input Validation | yes | Validate free text input (non-empty string); profile JSON schema validation on save |
| V6 Cryptography | no | No encryption needed; profile data is not sensitive (role, pain points, app preferences) |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Profile injection via free text | Tampering | LLM parses to structured JSON; no raw text stored as executable content |
| OAuth token leakage | Information Disclosure | Tokens stored in brain's integration clients, not in profile JSON; Phase 2 syncs to n8n securely |
| Onboarding bypass (skip to data) | Elevation of Privilege | Backend profile check is authoritative; no frontend-only bypass path |
| LLM prompt injection via Identity Box | Tampering | System prompt constrains output to JSON; profile validation rejects malformed responses |

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.13 | Backend (solo-leveling) | yes | 3.13 | -- |
| FastAPI | API endpoints | yes | existing | -- |
| Gemini API (run_agent) | Profile parsing, digest | yes | via GEMINI_API_KEY | -- |
| Node.js / npm | Dashboard build | yes | existing | -- |
| React 19 | Frontend components | yes | existing | -- |
| Tailwind CSS v4 | Styling | yes | existing | -- |
| Firebase Auth | OAuth + session | yes | existing | -- |

**Missing dependencies with no fallback:** none -- all dependencies are already available from prior phases.

**Missing dependencies with fallback:** none.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | OAuth flows for app connection can use popup-based approach (same as Phase 1 signInWithGoogle) | Pitfall 2 | May need full-page redirect with step persistence; increases complexity |
| A2 | Profile JSON can be stored in `data/profile.json` following local-first pattern | Pattern 3 | If Firestore is required, need dual-write like library entries |
| A3 | Digest generation can query gmail/youtube integration clients directly | Digest generation | If integration clients are not callable from onboarding context, need alternative data path |
| A4 | `run_agent()` returns valid JSON reliably enough for profile parsing | Pattern 2 | May need retry logic or fallback to keyword extraction |

## Open Questions (RESOLVED)

1. **OAuth popup vs redirect for app connection** (RESOLVED)
   - What we know: Phase 1 uses `signInWithGoogle()` which is popup-based
   - What's unclear: Whether the integration-specific OAuth flows (Gmail, YouTube) support popup-based authorization or require full-page redirect
   - RESOLVED: Plans use popup-based OAuth. Plan 01 Task 2 uses popup with backend step-save fallback (D-10). Plan 02 Task 2 uses popup with backend step-save before redirect fallback.

2. **Profile storage format** (RESOLVED)
   - What we know: Brain uses `data/` directory for JSON persistence (reminders, n8n_executions)
   - What's unclear: Whether profile should also be synced to Firestore like library entries
   - RESOLVED: Both plans use local-only `data/profile.json` pattern. Firestore sync deferred.

3. **Digest data source querying** (RESOLVED)
   - What we know: Integration clients (gmail, youtube) exist but are designed for command routing
   - What's unclear: Whether to call integration clients directly from the digest endpoint or go through the command router
   - RESOLVED: Plan 02 Task 1 calls integration clients directly via `_query_connected_sources()` — avoids command router overhead.

## Sources

### Primary (HIGH confidence)
- `dashboard/src/components/dashboard/DashboardPage.tsx` -- state lifting pattern, Panel A/B rendering
- `dashboard/src/components/guide/AIGuidePanel.tsx` -- Guide panel architecture
- `dashboard/src/components/zen/ZenShell.tsx` -- 70/30 layout
- `dashboard/src/components/zen/ContextNest.tsx` -- stream card pattern
- `dashboard/src/components/zen/StreamCard.tsx` -- card component
- `dashboard/src/components/ui/Button.tsx` -- button variants
- `dashboard/src/lib/api.ts` -- API client pattern
- `dashboard/src/styles/globals.css` -- design tokens
- `solo-leveling/src/agents/dispatcher.py` -- run_agent() pattern
- `solo-leveling/src/core/intent_parser.py` -- LLM structured output pattern
- `solo-leveling/src/api/guide.py` -- API endpoint pattern
- `solo-leveling/src/api/deps.py` -- require_auth dependency
- `solo-leveling/src/api/v1_router.py` -- router registration
- `solo-leveling/src/app.py` -- FastAPI app setup
- `solo-leveling/src/integrations/gmail/client.py` -- Gmail integration client
- `solo-leveling/src/core/config.py` -- configuration pattern
- `.planning/phases/05-onboarding-instant-win/05-CONTEXT.md` -- 15 locked decisions
- `.planning/phases/05-onboarding-instant-win/05-UI-SPEC.md` -- UI design contract
- `.planning/phases/03-knowledge-library/03-CONTEXT.md` -- Phase 3 decisions
- `.planning/phases/04-zen-shell/04-CONTEXT.md` -- Phase 4 decisions
- `.planning/phases/02-n8n-execution-layer/02-CONTEXT.md` -- Phase 2 decisions

### Secondary (MEDIUM confidence)
- `.planning/REQUIREMENTS.md` -- ONB-02, ONB-03, ONB-04 requirement definitions

### Tertiary (LOW confidence)
- OAuth popup behavior for non-Google integrations (assumption based on Phase 1 pattern)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all components already exist in codebase
- Architecture: HIGH -- follows established patterns from Phase 3 and 4
- Pitfalls: HIGH -- derived from actual codebase patterns and known integration behavior

**Research date:** 2026-05-31
**Valid until:** 2026-06-30 (stable -- depends on Phase 3/4 which are already implemented)
