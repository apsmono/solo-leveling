# Phase 5: Onboarding + Instant Win - Pattern Map

**Mapped:** 2026-05-31
**Files analyzed:** 14 (6 backend, 7 frontend, 1 modify)
**Analogs found:** 10 / 14

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `solo-leveling/src/api/onboarding.py` | controller | request-response | `solo-leveling/src/api/guide.py` | exact |
| `solo-leveling/src/api/profile.py` | controller | CRUD | `solo-leveling/src/api/reminders.py` | exact |
| `solo-leveling/src/api/v1_router.py` | config | — | (modify existing) | exact |
| `solo-leveling/src/core/profile_store.py` | service | CRUD | `solo-leveling/src/core/scheduler.py` (JSON persistence) | role-match |
| `solo-leveling/src/core/onboarding.py` | service | transform | `solo-leveling/src/core/intent_parser.py` | exact |
| `solo-leveling/tests/test_onboarding.py` | test | — | `solo-leveling/tests/test_guide_api.py` | exact |
| `dashboard/src/components/onboarding/OnboardingWizard.tsx` | component | request-response | `dashboard/src/components/zen/ContextNest.tsx` | role-match |
| `dashboard/src/components/onboarding/IdentityBox.tsx` | component | request-response | `dashboard/src/components/guide/AIGuidePanel.tsx` (input pattern) | partial |
| `dashboard/src/components/onboarding/ProfileConfirmation.tsx` | component | request-response | `dashboard/src/components/zen/StreamCard.tsx` | role-match |
| `dashboard/src/components/onboarding/AppConnectStep.tsx` | component | request-response | `dashboard/src/components/zen/StreamCard.tsx` | role-match |
| `dashboard/src/components/onboarding/InstantWinDigest.tsx` | component | request-response | `dashboard/src/components/zen/StreamCard.tsx` | exact |
| `dashboard/src/components/onboarding/StepIndicator.tsx` | component | — | (no analog — simple Tailwind dots) | none |
| `dashboard/src/hooks/useOnboarding.ts` | hook | request-response | `dashboard/src/hooks/useAuth.ts` | role-match |
| `dashboard/src/lib/api.ts` | utility | request-response | (modify existing) | exact |
| `dashboard/src/components/dashboard/DashboardPage.tsx` | component | request-response | (modify existing) | exact |

## Pattern Assignments

### `solo-leveling/src/api/onboarding.py` (controller, request-response)

**Analog:** `solo-leveling/src/api/guide.py`

**Imports pattern** (lines 1-27):
```python
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import require_auth
from src.agents.dispatcher import run_agent
from src.core.profile_store import load_profile, save_profile, save_onboarding_step

logger = logging.getLogger(__name__)

router = APIRouter()
```

**Auth + validation pattern** (lines 30-45 of guide.py):
```python
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
    # ... delegate to core/onboarding.py ...
    return {"status": "ok", "profile": parsed_profile}
```

**Error handling pattern** (lines 86-92 of guide.py):
```python
    except Exception:
        logger.exception("Failed to parse identity")
        return {
            "status": "error",
            "message": "Failed to parse identity. Please try again.",
        }
```

---

### `solo-leveling/src/api/profile.py` (controller, CRUD)

**Analog:** `solo-leveling/src/api/reminders.py`

**Imports pattern** (lines 1-16 of reminders.py):
```python
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import require_auth
from src.core.profile_store import load_profile, save_profile
```

**GET pattern** (lines 22-26 of reminders.py):
```python
@router.get("/profile")
async def get_profile(
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    profile = load_profile()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile found. Complete onboarding first.",
        )
    return {"status": "ok", "profile": profile}
```

**POST pattern** (lines 29-43 of reminders.py):
```python
@router.post("/profile")
async def create_profile(
    payload: dict[str, Any],
    _: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing profile data.",
        )
    save_profile(payload)
    return {"status": "ok", "profile": payload}
```

---

### `solo-leveling/src/api/v1_router.py` (config, modify)

**Analog:** existing file, lines 1-21

**Current registration pattern** (line 7 of v1_router.py):
```python
from src.api import dashboard, commands, reminders, library, graph, timeline, analysis, planning, autopilot, guide, n8n_callback
```

**Add these imports:**
```python
from src.api import onboarding, profile
```

**Add these registrations (after line 20):**
```python
router.include_router(onboarding.router)
router.include_router(profile.router)
```

---

### `solo-leveling/src/core/profile_store.py` (service, CRUD)

**Analog:** `solo-leveling/src/core/scheduler.py` (JSON file persistence pattern)

**Imports pattern** (lines 1-40 of scheduler.py):
```python
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_PROFILE_PATH = Path("data/profile.json")
```

**JSON persistence pattern** (extracted from scheduler.py data/ usage):
```python
def load_profile() -> dict[str, Any] | None:
    """Load profile from JSON file. Returns None if file doesn't exist."""
    if not _PROFILE_PATH.exists():
        return None
    try:
        return json.loads(_PROFILE_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        logger.warning("Failed to read profile from %s", _PROFILE_PATH)
        return None


def save_profile(profile: dict[str, Any]) -> None:
    """Save profile to JSON file."""
    _PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _PROFILE_PATH.write_text(json.dumps(profile, indent=2))
    logger.info("Profile saved to %s", _PROFILE_PATH)


def load_onboarding_step() -> int:
    """Return the last completed onboarding step (1-3). Defaults to 1."""
    profile = load_profile()
    if not profile:
        return 1
    return profile.get("onboarding_step", 1)


def save_onboarding_step(step: int) -> None:
    """Persist the current onboarding step."""
    profile = load_profile() or {}
    profile["onboarding_step"] = step
    save_profile(profile)
```

---

### `solo-leveling/src/core/onboarding.py` (service, transform)

**Analog:** `solo-leveling/src/core/intent_parser.py`

**Imports pattern** (lines 1-18 of intent_parser.py):
```python
from __future__ import annotations

import json
import logging
from typing import Any

from src.agents.dispatcher import run_agent

logger = logging.getLogger(__name__)
```

**LLM structured output pattern** (lines 71-129 of intent_parser.py):
```python
def parse_identity(text: str) -> dict[str, Any]:
    """Parse free text into a structured profile using LLM."""
    try:
        response = run_agent(
            task=f"Parse this identity description: {text}",
            system=_PROFILE_SYSTEM_PROMPT,
        )

        # Strip markdown code fences if LLM wrapped JSON
        cleaned = response.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        parsed = json.loads(cleaned)

        # Validate required fields
        result = {
            "role": str(parsed.get("role", "")),
            "pain_points": list(parsed.get("pain_points", []))[:3],
            "suggested_apps": list(parsed.get("suggested_apps", []))[:3],
            "context_templates": list(parsed.get("context_templates", [])),
            "needs_followup": bool(parsed.get("needs_followup", False)),
            "followup_question": str(parsed.get("followup_question", "")),
        }
        logger.info("Parsed identity: role=%s, apps=%s", result["role"], result["suggested_apps"])
        return result

    except Exception:
        logger.warning("Identity parser failed", exc_info=True)
        return {
            "role": "",
            "pain_points": [],
            "suggested_apps": [],
            "context_templates": [],
            "needs_followup": True,
            "followup_question": "Could you tell me a bit more about what you do and which apps you use most?",
        }
```

**System prompt constant** (modeled on lines 33-68 of intent_parser.py):
```python
_PROFILE_SYSTEM_PROMPT = """You are a profile parser for a personal command center.
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

**Digest generation pattern** (new, follows same run_agent pattern):
```python
def generate_digest(profile: dict[str, Any], connected_data: list[dict[str, Any]]) -> list[str]:
    """Generate 3-bullet digest from connected data sources."""
    context = json.dumps({"profile": profile, "data": connected_data}, indent=2)
    try:
        response = run_agent(
            task="Summarize the last 24 hours into exactly 3 concise bullet points.",
            context=context,
            system=_DIGEST_SYSTEM_PROMPT,
        )
        # Parse response as list of bullets
        cleaned = response.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        parsed = json.loads(cleaned)
        bullets = list(parsed.get("bullets", []))[:3]
        if len(bullets) < 3:
            bullets.extend(["No additional updates."] * (3 - len(bullets)))
        return bullets
    except Exception:
        logger.warning("Digest generation failed", exc_info=True)
        return [
            "Your streams are being set up.",
            "Data will appear here once connected sources sync.",
            "Check back in a few minutes.",
        ]
```

---

### `solo-leveling/tests/test_onboarding.py` (test)

**Analog:** `solo-leveling/tests/test_guide_api.py`

**Imports pattern** (lines 1-20 of test_guide_api.py):
```python
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app import app


class OnboardingAPITests(unittest.TestCase):
    """Contract tests for onboarding + profile endpoints."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_user = {"email": "owner@example.com", "uid": "abc123"}
```

**Test patterns** (from test_guide_api.py):
```python
    @patch("src.api.deps.verify_id_token")
    def test_parse_identity_returns_profile(self, mock_verify: MagicMock) -> None:
        """POST /api/v1/onboarding/parse-identity returns structured profile."""
        mock_verify.return_value = self.mock_user
        mock_profile = {
            "role": "Software engineer",
            "pain_points": ["too many emails"],
            "suggested_apps": ["gmail"],
            "context_templates": [],
            "needs_followup": False,
            "followup_question": "",
        }
        with patch("src.api.onboarding.parse_identity", return_value=mock_profile):
            response = self.client.post(
                "/api/v1/onboarding/parse-identity",
                json={"text": "I'm a software engineer drowning in emails"},
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("profile", data)

    @patch("src.api.deps.verify_id_token")
    def test_parse_identity_missing_text_returns_400(self, mock_verify: MagicMock) -> None:
        """POST /api/v1/onboarding/parse-identity with empty body returns 400."""
        mock_verify.return_value = self.mock_user
        response = self.client.post(
            "/api/v1/onboarding/parse-identity",
            json={},
            headers={"Authorization": "Bearer valid-token"},
        )
        self.assertEqual(response.status_code, 400)

    @patch("src.api.deps.verify_id_token")
    def test_get_profile_404_when_none(self, mock_verify: MagicMock) -> None:
        """GET /api/v1/profile returns 404 when no profile exists."""
        mock_verify.return_value = self.mock_user
        with patch("src.api.profile.load_profile", return_value=None):
            response = self.client.get(
                "/api/v1/profile",
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 404)

    @patch("src.api.deps.verify_id_token")
    def test_get_profile_returns_existing(self, mock_verify: MagicMock) -> None:
        """GET /api/v1/profile returns profile when it exists."""
        mock_verify.return_value = self.mock_user
        mock_profile = {"role": "Engineer", "pain_points": [], "suggested_apps": []}
        with patch("src.api.profile.load_profile", return_value=mock_profile):
            response = self.client.get(
                "/api/v1/profile",
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["profile"]["role"], "Engineer")

    @patch("src.api.deps.verify_id_token")
    def test_cold_start_digest_returns_capability_preview(self, mock_verify: MagicMock) -> None:
        """GET /api/v1/onboarding/digest with no data returns capability preview."""
        mock_verify.return_value = self.mock_user
        with patch("src.api.onboarding._query_connected_sources", return_value=[]):
            response = self.client.get(
                "/api/v1/onboarding/digest",
                headers={"Authorization": "Bearer valid-token"},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(len(data["bullets"]), 3)
```

---

### `dashboard/src/components/onboarding/OnboardingWizard.tsx` (component, request-response)

**Analog:** `dashboard/src/components/zen/ContextNest.tsx` (container component pattern)

**Imports pattern** (lines 1-4 of ContextNest.tsx):
```typescript
import { useState, useCallback } from "react";
import { IdentityBox } from "./IdentityBox";
import { ProfileConfirmation } from "./ProfileConfirmation";
import { AppConnectStep } from "./AppConnectStep";
import { InstantWinDigest } from "./InstantWinDigest";
import { StepIndicator } from "./StepIndicator";
import { Button } from "@/components/ui/Button";
import type { ProfileData, OnboardingStep } from "./types";
```

**Container render pattern** (lines 73-92 of ContextNest.tsx):
```tsx
interface OnboardingWizardProps {
  step: OnboardingStep;
  profile: ProfileData | null;
  onStepChange: (step: OnboardingStep) => void;
  onComplete: () => void;
  onProfileParsed: (profile: ProfileData) => void;
}

export function OnboardingWizard({
  step,
  profile,
  onStepChange,
  onComplete,
  onProfileParsed,
}: OnboardingWizardProps) {
  return (
    <section aria-label="Onboarding" className="flex flex-col gap-4 p-4">
      <StepIndicator current={step} total={3} />
      {step === 1 && (
        <IdentityBox onProfileParsed={onProfileParsed} onNext={() => onStepChange(2)} />
      )}
      {step === 2 && profile && (
        <ProfileConfirmation
          profile={profile}
          onConfirm={() => onStepChange(3)}
          onEdit={(updated) => onProfileParsed(updated)}
        />
      )}
      {step === 2 && profile && (
        <AppConnectStep
          suggestedApps={profile.suggested_apps}
          onSkip={() => onStepChange(3)}
          onConnected={() => onStepChange(3)}
        />
      )}
      {step === 3 && (
        <InstantWinDigest profile={profile} onComplete={onComplete} />
      )}
    </section>
  );
}
```

---

### `dashboard/src/components/onboarding/IdentityBox.tsx` (component, request-response)

**Analog:** `dashboard/src/components/guide/AIGuidePanel.tsx` (text input + submit pattern)

**Core pattern** — text input with loading state:
```tsx
import { useState, useCallback } from "react";
import { Button } from "@/components/ui/Button";
import { Sparkles } from "lucide-react";
import { parseIdentity } from "@/lib/api";
import type { ProfileData } from "./types";

interface IdentityBoxProps {
  onProfileParsed: (profile: ProfileData) => void;
  onNext: () => void;
}

export function IdentityBox({ onProfileParsed, onNext }: IdentityBoxProps) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [followup, setFollowup] = useState<string | null>(null);

  const handleSubmit = useCallback(async () => {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const result = await parseIdentity(text.trim());
      if (result.profile.needs_followup && !followup) {
        setFollowup(result.profile.followup_question);
        setLoading(false);
        return;
      }
      onProfileParsed(result.profile);
      onNext();
    } catch (err) {
      console.error("Identity parse failed:", err);
    } finally {
      setLoading(false);
    }
  }, [text, followup, onProfileParsed, onNext]);

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-lg font-semibold text-text">Tell me about yourself</h2>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Tell me what you do and what overwhelms you..."
        className="min-h-[100px] w-full rounded-lg border border-border bg-card p-3 text-sm text-text placeholder:text-muted focus:border-accent focus:outline-none"
        disabled={loading}
      />
      {followup && (
        <p className="text-sm text-muted italic">{followup}</p>
      )}
      <Button
        onClick={handleSubmit}
        disabled={!text.trim() || loading}
        className="w-full"
      >
        {loading ? (
          <span className="inline-flex items-center gap-2">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
            Analyzing...
          </span>
        ) : (
          <span className="inline-flex items-center gap-2">
            <Sparkles size={14} />
            {followup ? "Continue" : "Analyze"}
          </span>
        )}
      </Button>
    </div>
  );
}
```

---

### `dashboard/src/components/onboarding/ProfileConfirmation.tsx` (component, request-response)

**Analog:** `dashboard/src/components/zen/StreamCard.tsx` (card layout with bullets)

**Card styling pattern** (lines 45-48 of StreamCard.tsx):
```tsx
<article className="flex flex-col rounded-lg border bg-card p-3 shadow-sm border-border">
  <div className="mb-2 flex items-center justify-between text-xs text-muted">
    <span className="inline-flex items-center gap-1.5 font-medium">
      <Sparkles size={14} className="text-accent" />
      Your Profile
    </span>
  </div>
  <ul className="mb-2 flex-1 space-y-0.5 text-sm text-text">
    <li>Role: {profile.role}</li>
    {profile.pain_points.map((p, i) => (
      <li key={i}>Pain point: {p}</li>
    ))}
    {profile.suggested_apps.map((a, i) => (
      <li key={`app-${i}`}>Suggested app: {a}</li>
    ))}
  </ul>
  <div className="flex gap-2">
    <Button variant="primary" onClick={onConfirm}>Looks good</Button>
    <Button variant="secondary" onClick={() => setEditing(true)}>Edit</Button>
  </div>
</article>
```

---

### `dashboard/src/components/onboarding/AppConnectStep.tsx` (component, request-response)

**Analog:** `dashboard/src/components/zen/StreamCard.tsx` (card layout per app)

**Card pattern per app** (adapted from StreamCard):
```tsx
<div className="flex flex-col gap-2">
  <h3 className="text-sm font-medium text-text">Connect your apps</h3>
  {suggestedApps.map((app) => (
    <article key={app} className="flex items-center justify-between rounded-lg border border-border bg-card p-3">
      <span className="text-sm text-text">{app}</span>
      <Button variant="secondary" size="sm" onClick={() => handleConnect(app)}>
        Connect
      </Button>
    </article>
  ))}
  <button type="button" onClick={onSkip} className="text-sm text-muted hover:text-accent">
    Skip for now
  </button>
</div>
```

---

### `dashboard/src/components/onboarding/InstantWinDigest.tsx` (component, request-response)

**Analog:** `dashboard/src/components/zen/StreamCard.tsx` (exact match — 3-bullet card)

**Card pattern** (lines 34-78 of StreamCard.tsx, adapted):
```tsx
<article className="flex max-h-[140px] flex-col rounded-lg border bg-card p-3 shadow-sm border-border">
  <div className="mb-2 flex items-center justify-between text-xs text-muted">
    <span className="inline-flex items-center gap-1.5 font-medium">
      <Sparkles size={14} className="text-accent" />
      Your first digest
    </span>
    <span>Last 24 hours</span>
  </div>
  <ul className="mb-2 flex-1 space-y-0.5 overflow-hidden text-sm text-text">
    {bullets.map((bullet, i) => (
      <li key={i} className="truncate">{"bull;"} {bullet}</li>
    ))}
  </ul>
  <Button variant="primary" onClick={onComplete}>
    Get started
  </Button>
</article>
```

---

### `dashboard/src/components/onboarding/StepIndicator.tsx` (component, no analog)

**No close analog in codebase.** Simple Tailwind component:

```tsx
interface StepIndicatorProps {
  current: number;
  total: number;
}

export function StepIndicator({ current, total }: StepIndicatorProps) {
  return (
    <div className="flex items-center justify-center gap-2" aria-label={`Step ${current} of ${total}`}>
      {Array.from({ length: total }, (_, i) => (
        <div
          key={i}
          className={`h-2 w-2 rounded-full transition-colors ${
            i + 1 <= current ? "bg-accent" : "bg-border"
          }`}
        />
      ))}
    </div>
  );
}
```

---

### `dashboard/src/hooks/useOnboarding.ts` (hook, request-response)

**Analog:** `dashboard/src/hooks/useAuth.ts`

**Hook pattern** (lines 1-35 of useAuth.ts):
```typescript
import { useState, useEffect, useCallback } from "react";
import { apiGet } from "@/lib/api";
import type { ProfileData } from "@/components/onboarding/types";

type OnboardingState = "loading" | "onboarding" | "complete";
type OnboardingStep = 1 | 2 | 3;

export function useOnboarding() {
  const [state, setState] = useState<OnboardingState>("loading");
  const [step, setStep] = useState<OnboardingStep>(1);
  const [profile, setProfile] = useState<ProfileData | null>(null);

  // First-run detection on mount (D-08: backend profile check)
  useEffect(() => {
    apiGet<{ status: string; profile: ProfileData }>("/api/v1/profile")
      .then((res) => {
        setProfile(res.profile);
        setState("complete");
      })
      .catch((err) => {
        if (err.message?.includes("404")) {
          setState("onboarding");
        } else {
          // Network error — skip onboarding, don't block the user
          setState("complete");
        }
      });
  }, []);

  const handleProfileParsed = useCallback((p: ProfileData) => {
    setProfile(p);
  }, []);

  const handleStepChange = useCallback((newStep: OnboardingStep) => {
    setStep(newStep);
  }, []);

  const handleComplete = useCallback(() => {
    setState("complete");
  }, []);

  return {
    state,
    step,
    profile,
    handleProfileParsed,
    handleStepChange,
    handleComplete,
  };
}
```

---

### `dashboard/src/lib/api.ts` (utility, modify — add onboarding API functions)

**Analog:** existing file, lines 480-500 (Guide API section)

**Add after Guide API section** (after line 500):
```typescript
// ---------------------------------------------------------------------------
// Onboarding API
// ---------------------------------------------------------------------------

export interface ProfileData {
  role: string;
  pain_points: string[];
  suggested_apps: string[];
  context_templates: string[];
  needs_followup: boolean;
  followup_question: string;
}

export interface ParseIdentityResponse {
  status: string;
  profile: ProfileData;
}

export async function parseIdentity(text: string): Promise<ParseIdentityResponse> {
  return apiPost<ParseIdentityResponse>("/api/v1/onboarding/parse-identity", { text });
}

export async function fetchProfile(): Promise<{ status: string; profile: ProfileData }> {
  return apiGet<{ status: string; profile: ProfileData }>("/api/v1/profile");
}

export async function saveProfile(profile: ProfileData): Promise<{ status: string; profile: ProfileData }> {
  return apiPost<{ status: string; profile: ProfileData }>("/api/v1/profile", profile);
}

export async function connectApp(appName: string): Promise<{ status: string; auth_url?: string }> {
  return apiPost<{ status: string; auth_url?: string }>("/api/v1/onboarding/connect-app", { app: appName });
}

export async function fetchDigest(): Promise<{ status: string; bullets: string[] }> {
  return apiGet<{ status: string; bullets: string[] }>("/api/v1/onboarding/digest");
}

export async function saveOnboardingStep(step: number): Promise<{ status: string }> {
  return apiPost<{ status: string }>("/api/v1/profile/onboarding-step", { step });
}
```

---

### `dashboard/src/components/dashboard/DashboardPage.tsx` (component, modify)

**Analog:** existing file (lines 1-441)

**Integration point** — add onboarding state and conditional Panel A render:

**Add imports** (near line 14):
```typescript
import { OnboardingWizard } from "@/components/onboarding/OnboardingWizard";
import { useOnboarding } from "@/hooks/useOnboarding";
```

**Add hook call** (inside DashboardPageContent, near line 125):
```typescript
const { state: onboardingState, step: onboardingStep, profile, handleProfileParsed, handleStepChange, handleComplete } = useOnboarding();
```

**Modify Panel A render** (replace the ClarityBoard conditional around line 313):
```tsx
{onboardingState === "onboarding" ? (
  <OnboardingWizard
    step={onboardingStep}
    profile={profile}
    onStepChange={handleStepChange}
    onComplete={handleComplete}
    onProfileParsed={handleProfileParsed}
  />
) : moreTab ? (
  // ... existing moreTab Suspense block ...
) : (
  <ClarityBoard ... />
)}
```

**Loading state** (line 187-193): Also show spinner when `onboardingState === "loading"`:
```tsx
if (loading || onboardingState === "loading") {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
    </div>
  );
}
```

---

## Shared Patterns

### Authentication
**Source:** `solo-leveling/src/api/deps.py`
**Apply to:** All onboarding and profile endpoints
```python
from src.api.deps import require_auth

@router.post("/endpoint")
async def handler(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    ...
```

### Error Handling (Backend)
**Source:** `solo-leveling/src/api/guide.py` lines 86-92
**Apply to:** All onboarding endpoints
```python
    except Exception:
        logger.exception("Failed to <action>")
        return {
            "status": "error",
            "message": "User-friendly error message.",
        }
```

### Input Validation (Backend)
**Source:** `solo-leveling/src/api/guide.py` lines 36-41
**Apply to:** All POST endpoints accepting text
```python
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'text' in request payload.",
        )
```

### API Client (Frontend)
**Source:** `dashboard/src/lib/api.ts` lines 20-34
**Apply to:** All frontend onboarding API calls
```typescript
import { apiGet, apiPost } from "@/lib/api";

// GET: apiGet<T>("/api/v1/...")
// POST: apiPost<T>("/api/v1/...", body)
```

### Button Component (Frontend)
**Source:** `dashboard/src/components/ui/Button.tsx`
**Apply to:** All CTAs in onboarding wizard
```typescript
import { Button } from "@/components/ui/Button";
// Variants: "primary" | "secondary" | "ghost" | "danger"
// Sizes: "sm" | "md" | "lg"
```

### Card Styling (Frontend)
**Source:** `dashboard/src/components/zen/StreamCard.tsx` lines 45-48
**Apply to:** ProfileConfirmation, AppConnectStep, InstantWinDigest
```tsx
<article className="flex max-h-[140px] flex-col rounded-lg border bg-card p-3 shadow-sm border-border">
```

## No Analog Found

Files with no close match in the codebase (planner should use RESEARCH.md patterns instead):

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `dashboard/src/components/onboarding/StepIndicator.tsx` | component | — | Simple dots indicator; no existing progress/stepper component in codebase |
| `dashboard/src/components/onboarding/types.ts` | types | — | New type definitions for ProfileData, OnboardingStep |

## Metadata

**Analog search scope:** `solo-leveling/src/api/`, `solo-leveling/src/core/`, `solo-leveling/tests/`, `dashboard/src/components/`, `dashboard/src/hooks/`, `dashboard/src/lib/`
**Files scanned:** 28
**Pattern extraction date:** 2026-05-31
