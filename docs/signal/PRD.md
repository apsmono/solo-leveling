# Signal — Product Requirement Document (PRD)

**Project Code Name:** Signal
**Phase:** MVP v1.0 → v1.5
**Last Updated:** 2026-05-30
**Status:** Living Document — Engineering Ready

---

## Table of Contents

1. [Problem Statement & Market Opportunity](#1-problem-statement--market-opportunity)
2. [User Persona](#2-user-persona)
3. [Current State Assessment](#3-current-state-assessment)
4. [Architecture](#4-architecture)
5. [Feature Ecosystem](#5-feature-ecosystem)
6. [Security Architecture & Threat Model](#6-security-architecture--threat-model)
7. [Testing Strategy & Quality Assurance](#7-testing-strategy--quality-assurance)
8. [Resilience, Error Mitigation & Observability](#8-resilience-error-mitigation--observability)
9. [User Flow Architecture & State Machines](#9-user-flow-architecture--state-machines)
10. [UI/UX Design System & Interaction Patterns](#10-uiux-design-system--interaction-patterns)
11. [API Contract](#11-api-contract)
12. [Monetization & Subscription Strategy](#12-monetization--subscription-strategy)
13. [Implementation Roadmap](#13-implementation-roadmap)
14. [Decision Log & Risk Matrix](#14-decision-log--risk-matrix)
15. [Glossary](#15-glossary)

---

## 1. Problem Statement & Market Opportunity

In the hyper-digital era, individuals and professionals suffer from intense "infobesity" — an overwhelming daily influx of unstructured data (emails, chats, RSS feeds, market metrics). This triggers cognitive fatigue, severe analysis paralysis, and chronic procrastination.

Existing automation tools fall short because they are either highly technical developer-first canvases (requiring complex logic trees and API configurations) or unpredictable and expensive (such as hiring an unverified virtual assistant).

**The Core Pain Point:** Users spend hours performing low-level cognitive labor — filtering, sorting, and summarizing raw information — leaving them with no energy for high-value strategic execution.

**Signal's Answer:** A personal AI command center that ingests noise, extracts signal, and presents calm, actionable intelligence — all without the user managing integrations, writing code, or handling raw API keys.

---

## 2. User Persona

### The "High-Output Minimalist"

- **Who they are:** Business owners, freelancers, and high-performing professionals who value their time over money. They are willing to pay a premium subscription to protect their focus.
- **Tech Literacy:** Moderate. They use modern apps daily but demand a "plug-and-play" experience. They want to avoid writing code, managing integrations, or mastering complex prompt engineering.
- **Behavioral Goal:** Survive and thrive in a rapid-pace market by staying cleanly informed, without managing ten different communications tabs.
- **Primary Device:** Mobile-first (Telegram Mini App), with desktop as secondary.

### Owner Profile (Development Phase)

- Single owner: `pramono@getgoing.co.id`
- MacMini as primary backend host (Docker Compose)
- Firebase project: `apsmono-projects`
- Integrations: Gmail, Google Drive, Notion, GitHub, Telegram, Discord

---

## 3. Current State Assessment

### 3.1 What Exists Today

| Component | Status | Details |
|-----------|--------|---------|
| **Backend Brain** (solo-leveling) | Production | FastAPI on MacMini via Docker, 59+ tests passing |
| **Command Router** | Production | ~25 intents, keyword + LLM-based detection |
| **Library System** (Stage 9) | Production | File-based markdown knowledge store with vector search |
| **Vector DB** | Production | pgvector on PostgreSQL, Gemini embeddings, hybrid search |
| **Integrations** | Production | Gmail, Google Drive, Notion, GitHub, Telegram, Discord |
| **Autopilot** | Phase 2 Complete | Goal → step planning, RL1-5 governance, tool registry |
| **Dashboard Frontend** | Production | React 19 + Vite + Tailwind, deployed to GitHub Pages |
| **Firebase Auth** | Production | Google OAuth popup, session cookies, single-user gate |
| **Telegram Bot** | Production | Webhook-based, proactive messaging, CLI management |
| **AI Guide** | Production | `/api/v1/guide/*` endpoints, command parsing, status metrics |
| **n8n** | Scaffolded | Docker Compose config exists, not yet wired to brain |
| **Smart Feeds** | Not Started | YouTube abstraction planned, no implementation |
| **Smart Drafts** | Not Started | Context-aware reply generation planned |

### 3.2 Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend Framework | FastAPI + Uvicorn | Python 3.13 |
| HTTP Client | httpx | Latest |
| Scheduling | APScheduler | Latest |
| AI Provider (Primary) | Gemini (gemini-2.0-flash) | REST via httpx |
| AI Provider (Autopilot) | Kimi | via litellm |
| Vector Database | PostgreSQL + pgvector | pg16 |
| Embeddings | Gemini embedding-001 | 768-dim |
| Frontend Framework | React 19 + TypeScript 6 | Vite 8 |
| CSS | Tailwind CSS 4 | Via Vite plugin |
| Auth | Firebase Auth | Google OAuth |
| Container | Docker Compose | Python 3.13-slim |
| Workflow Engine | n8n | Docker (planned) |

### 3.3 Deployment Topology

```
                    apsmono/projects (parent repo)
                             │ pins SHAs
        ┌────────────┬───────┼───────┬──────────────────┐
        ▼            ▼       ▼       ▼                  ▼
  solo-leveling   dashboard  apsmono  wedding-invitation  koperasi
  (FastAPI brain) (React UI) .github  (React SPA)       (static)
       │              ▲      .io
       │              │
       └── REST /api/v1 + /command (Firebase-auth'd) ──┘
       
  MacMini (Docker Compose): brain + n8n + pgvector
  GitHub Pages: dashboard + portfolio
  Cloudflare Pages: koperasi
```

---

## 4. Architecture

### 4.1 System Architecture (Current)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    solo-leveling FastAPI Process                     │
│                                                                     │
│  Command Interface                                                  │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐ │
│  │ POST /command │  │ /webhook/telegram│  │ /api/v1/* (Firebase) │ │
│  └──────┬───────┘  └────────┬─────────┘  └──────────┬───────────┘ │
│         │                   │                        │             │
│  ┌──────▼───────────────────▼────────────────────────▼───────────┐ │
│  │ Brain Core                                                    │ │
│  │ • router.py — intent detection (keyword + LLM)                │ │
│  │ • libraries.py — Stage 9 knowledge store                      │ │
│  │ • workflows.py — multi-step integration chains                │ │
│  │ • scheduler.py — APScheduler background jobs                  │ │
│  └──────┬────────────────────────────────────────────────────────┘ │
│         │                                                          │
│  ┌──────▼────────────────────────────────────────────────────────┐ │
│  │ AI Agent Layer                                                │ │
│  │ • agents/dispatcher.py — Gemini REST wrapper                  │ │
│  │ • agents/kimi_client.py — Kimi via litellm                    │ │
│  │ • autopilot/ — planner · governor · tools · loop              │ │
│  └──────┬────────────────────────────────────────────────────────┘ │
│         │                                                          │
│  ┌──────▼────────────────────────────────────────────────────────┐ │
│  │ Integration Layer                                             │ │
│  │ • notion/ gdrive/ gmail/ firebase/ github/ telegram/ discord/ │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ Vector Layer                                                  │ │
│  │ • vector/db.py — async pgvector pool                          │ │
│  │ • vector/embed.py — Gemini embedding client                   │ │
│  │ • vector/search.py — hybrid keyword + vector search           │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
        │ local-first state
        ▼
  library/ (markdown + index.json)   data/ (reminders, autopilot tasks)
  PostgreSQL + pgvector (vector spine)   Firebase Firestore (optional)
```

### 4.2 Target Architecture (v1.0)

The target adds three major layers:

1. **n8n Execution Layer** — Brain translates owner intents into n8n workflow executions via REST API. Credential injection pushes OAuth tokens into n8n's store. Execution status ingested via webhook callbacks.

2. **Smart Feed Layer** — YouTube transcript abstraction, news deduplication, RSS processing. All feed items compressed into 3-bullet cards via LLM.

3. **Smart Draft Layer** — Context-aware reply generation. Fetches email thread + user style profile + relationship context. Presents draft with tone variants.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Signal v1.0 Target Architecture                   │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │ Telegram    │  │ Dashboard   │  │ Webhook     │                │
│  │ Mini App    │  │ (React)     │  │ Callbacks   │                │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                │
│         │                │                 │                        │
│  ┌──────▼────────────────▼─────────────────▼──────────────────────┐ │
│  │ Command Interface (FastAPI)                                    │ │
│  └──────┬────────────────────────────────────────────────────────┘ │
│         │                                                          │
│  ┌──────▼────────────────────────────────────────────────────────┐ │
│  │ Brain Core + AI Agent Layer                                   │ │
│  │ • Intent → template matching (hybrid LLM + skeleton)          │ │
│  │ • RL approval gate for side-effecting actions                 │ │
│  │ • Error abstraction layer (soft messages)                     │ │
│  └──────┬────────────────────────────────────────────────────────┘ │
│         │                                                          │
│  ┌──────▼────────────────────────────────────────────────────────┐ │
│  │ n8n Execution Layer                                           │ │
│  │ • Workflow triggering (REST API)                              │ │
│  │ • Credential injection (OAuth → n8n credential store)         │ │
│  │ • Execution status ingestion (webhook callbacks)              │ │
│  │ • Template skeleton catalog                                   │ │
│  └──────┬────────────────────────────────────────────────────────┘ │
│         │                                                          │
│  ┌──────▼────────────────────────────────────────────────────────┐ │
│  │ Smart Feeds + Smart Drafts                                    │ │
│  │ • YouTube transcript abstraction                              │ │
│  │ • News deduplication (vector similarity)                      │ │
│  │ • Context-aware reply generation                              │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.3 Three Execution Patterns

1. **Synchronous Dispatch** — Command arrives → `route_command()` detects intent → handler runs → reply returned. Default path for `/command` and Telegram.

2. **Asynchronous Automation** — `scheduler.py` (APScheduler) runs background jobs: due reminders, daily Gmail digest, weekly library maintenance.

3. **Autonomous Loop (Autopilot)** — Goal planned into steps by Gemini → task persisted → ticker advances one step at a time → Governor checks RL level → execute tool → record observation → advance.

### 4.4 State & Persistence (Local-First)

| Data | Location | Persistence |
|------|----------|-------------|
| Knowledge entries | `library/` markdown files | Git + Docker volume |
| Library index | `library/index.json` | Regenerated on write |
| Vector embeddings | PostgreSQL + pgvector | Docker volume |
| Reminders | `data/reminders.json` | Docker volume |
| Autopilot state | `data/autopilot_*.json` | Docker volume |
| Command history | Firebase Firestore | Optional dual backend |
| n8n execution logs | `data/n8n_executions.json` | Docker volume (planned) |
| Unmet intents | `data/unmet_intents.json` | Docker volume (planned) |

---

## 5. Feature Ecosystem

### 5.1 Pillar 1: Smart Feed Subscriptions (Noise-Free Consumption)

**Status:** Not Started (Phase 6-7)

- **YouTube Abstraction:** n8n backend processes pull video transcriptions silently. The internal LLM compresses the transcript into a 3-bullet-point takeaway card with reading time metrics.
- **News Deduplication:** Collates matching events into a single situational update card using vector similarity (>0.85 threshold → merge).
- **RSS Feed Processing:** Configurable feed subscriptions. New items queued silently for designated reading routines.
- **Controlled Notification Rules:** Disables push alerts entirely; new content queues up silently for designated reading routines.

### 5.2 Pillar 2: Core Automation & Shadow Work Execution

**Status:** Partially Implemented

- **Command Routing:** 25+ intents with keyword + LLM-based detection. Works via HTTP `/command` and Telegram webhook.
- **Multi-Step Workflows:** Gmail → Notion, Gmail → summary, and other chained integrations (Stage 8).
- **Autopilot:** Goal → step planning with RL1-5 governance. Tools: read, bash, edit, write, claude_code, web_search, gmail_read, notion_create, gdrive_create, library_index, git_commit, telegram_notify.
- **Smart Drafts (Planned):** Context-aware, writing-style-matching response drafts. One-click options: Approve & Send, Make Friendlier, Make Firmer.
- **Keep-In-Touch Pulse (Planned):** Monitors relationship logs and proactively drafts relationship maintenance touchpoints.

### 5.3 Pillar 3: Knowledge Library (Stage 9)

**Status:** Production

- **File-Based Storage:** Markdown files organized by section (profile, terms, books, articles, thoughts, references, research).
- **Deep Capture:** AI-assisted "add to library" flow. Gemini analyzes content → creates research bundle (7 markdown files) + auto-creates supporting entries.
- **Hybrid Search:** Keyword search (in-memory LRU cache with TTL) + vector search (pgvector with Gemini embeddings). Modes: keyword, vector, hybrid.
- **Graph Visualization:** Nodes + edges for knowledge graph. Colors by section, edges by shared tags.
- **Timeline View:** Chronological stream of library entries with daily counts.
- **Analysis:** Tag frequencies, trending tags, orphan detection, section gaps, activity velocity.
- **AI Synthesis:** Cross-entry Q&A using Gemini with source citations.

### 5.4 Pillar 4: Planning & Habits

**Status:** Production

- **Goals:** Hierarchical goal tracking with parent_id, progress percentage, status (active/completed/paused).
- **Projects:** Active/completed project tracking.
- **Tasks:** CRUD with priority (high/medium/low), due dates, goal/project association.
- **Habits:** Daily check-in tracking with streak counting, frequency settings, color coding.
- **Weekly Reviews:** AI-generated review with wins, gaps, and next focus suggestions.
- **Focus Suggestions:** AI-suggested priorities based on active goals and recent activity.

### 5.5 Pillar 5: Advanced Customization ("YOLO Mode")

**Status:** Deferred to v1.1

- **Custom LLM Injection:** Bypass native models to let users plug in their own direct OpenAI or Anthropic API keys.
- **Direct Node Canvas / JSON Access:** Expose the raw n8n workflow JSON strings for manual execution, custom JavaScript node code injection, or custom endpoint hooks.
- **Guardrail Disabling:** Permit full automation dispatch bypassing the default human-in-the-loop review requirement.

### 5.6 Pillar 6: n8n Execution Layer

**Status:** Scaffolded (Phase 2)

- **Workflow Triggering:** Brain translates owner intents into n8n workflow executions via REST API (`POST /api/v1/workflows/{id}/run`).
- **Credential Injection:** Brain populates n8n's own credential store via API. Workflows reference credentials by ID. Owner never sees raw keys.
- **Execution Status Ingestion:** n8n webhook callbacks POST results to brain's FastAPI endpoint. Hybrid: polling for short workflows, webhook for long ones.
- **Error Abstraction:** Translates technical n8n/backend errors into soft, actionable AI-Guide messages.
- **RL Approval Gate:** Side-effecting workflows (send, post, modify) pass through existing RL governor. Read-only runs execute freely.

---

## 6. Security Architecture & Threat Model

### 6.1 Threat Model (STRIDE Framework)

| Threat Category | Asset | Attack Vector | Mitigation | Priority |
|----------------|-------|---------------|------------|----------|
| Spoofing | User identity | OAuth token theft | PKCE + state param for OAuth; short-lived JWTs (15min); refresh token rotation | P0 |
| Tampering | Workflow JSON, user data | MITM, supply chain | TLS 1.3 everywhere; signed webhooks (HMAC-SHA256); dependency pinning + SCA scanning | P0 |
| Repudiation | Automated actions | User claims "I didn't send that" | Immutable audit logs (WORM storage); digital signatures on all dispatched actions | P0 |
| Information Disclosure | OAuth tokens, LLM prompts | DB breach, log leakage | AES-256-GCM encryption at rest; token vault with zero-knowledge proxy; PII redaction in logs | P0 |
| Denial of Service | LLM API, n8n engine | Token exhaustion, infinite loops | Rate limiting per user (token bucket); circuit breakers on LLM calls; execution timeouts (30s max) | P1 |
| Elevation of Privilege | YOLO Mode | RCE via injected custom code | Sandboxed JS/Python execution (gVisor/Firecracker); denylist for dangerous modules; AST analysis | P0 |

### 6.2 Authentication & Authorization

#### Current Implementation

- **Firebase Auth:** Google OAuth popup, ID token as Bearer header on all `/api/v1/*` endpoints.
- **Session Cookies:** Firebase session cookie auth (`/auth/session-login`, `/auth/session-logout`) with httpOnly Secure SameSite=Strict cookies.
- **Single-User Gate:** `ALLOWED_USER_EMAIL` in brain `.env` must match the Google account used in the dashboard.

#### Target Implementation (v1.0)

- **PKCE (Proof Key for Code Exchange):** Mandatory for all OAuth flows — prevents authorization code interception attacks.
- **State Parameter with CSRF Nonce:** 32-byte random, validated server-side, single-use, 10min TTL.
- **Scope Minimization:** Request only scopes strictly needed. Gmail: `gmail.readonly` + `gmail.send` (send only for Smart Drafts). Never request full mailbox control.
- **Token Vault (Zero-Knowledge Proxy):**
  - Encryption: AES-256-GCM with envelope encryption
  - Key Hierarchy: Data Encryption Key (DEK) per-user, rotated 90 days; Key Encryption Key (KEK) in KMS; Root Key in HSM
  - Access Pattern: Backend requests token → Vault decrypts → Token returned via mTLS → Backend zeroes memory after use
  - Audit: Every decrypt operation logged with timestamp, user_id, service_name, reason_code

#### Role-Based Access Control (RBAC)

| Resource | user | admin | system |
|----------|------|-------|--------|
| Own workflows | CRUD | R | R |
| Own tokens | — | — | R* |
| Own digest content | R | R** | R |
| Other user data | — | — | — |
| System configs | — | — | CRUD |

*system reads only from vault, never stores
**admin reads only with explicit user consent + ticket number

### 6.3 Data Protection & Privacy

#### Data Classification

| Class | Examples | Storage | Retention | Encryption |
|-------|----------|---------|-----------|------------|
| Critical | OAuth tokens, API keys | Token Vault (HSM-backed) | Until revoked + 30 days | AES-256-GCM + envelope |
| Sensitive | Email content, chat logs, personal notes | Encrypted DB (per-user keys) | User-controlled + 90 days post-deletion | AES-256-GCM |
| Personal | Name, email, usage patterns | Standard DB | Account lifetime + 30 days | At-rest (AES-256) |
| Public | News articles, RSS content | Cached object storage | 48 hours | TLS in transit only |

#### LLM Data Handling

- **Zero-Retention Enforcement:** Anthropic Claude (default, API data not used for training); Gemini (opt-out required); local models (fully private).
- **Data Minimization for LLM Prompts:**
  - Pre-processing pipeline strips PII before sending to LLM: emails → `[EMAIL_1]`, phones → `[PHONE_1]`, names → `[PERSON_1]`
  - Context window limits: Never send >50 emails or >10,000 tokens per digest generation
  - System prompt explicitly instructs: "Do not memorize or reproduce user data. This is a stateless processing request."

#### GDPR / CCPA Compliance

| Requirement | Implementation |
|-------------|----------------|
| Right to Access | `/api/v1/user/data-export` — returns ZIP with all user data |
| Right to Deletion | `/api/v1/user/delete` — cascades through token revocation → workflow deletion → vector DB purge → DB anonymization. 30-day grace period |
| Right to Portability | Export in JSON (machine-readable) + PDF (human-readable) |
| Consent Management | Granular consent per integration with separate toggle + timestamp + version |
| Breach Notification | 72-hour internal SLA; 72-hour regulatory notification; immediate user email if Critical/Sensitive class affected |

### 6.4 Network Security

- **WAF Rules:** OWASP Top 10 + custom rules for LLM prompt injection patterns
- **Rate Limiting:** Token bucket per user_id + IP. Free: 10 req/min. Pro: 100 req/min. Business: 500 req/min.
- **mTLS:** All internal service communication requires SPIFFE/SPIRE-issued certificates
- **Network Segmentation:** Worker pods in private subnet with no public IP. NAT Gateway for outbound only.
- **Egress Filtering:** Worker pods can reach only: LLM APIs (allowlisted IPs), OAuth providers, email APIs. Default deny all other outbound.

### 6.5 Webhook Security

All incoming webhooks must:
1. Verify signature using provider's public key
2. Idempotency check — deduplicate via Message-Id or webhook payload hash (Redis 24h TTL)
3. Replay protection — reject timestamps >5 minutes old
4. IP allowlisting — only accept from known provider IP ranges

---

## 7. Testing Strategy & Quality Assurance

### 7.1 Testing Pyramid

```
┌─────────┐
│ E2E     │ ← 5% of tests, highest confidence
│(Playwright) Full user journey simulation
├─────────┤
│Integration│ ← 15% of tests
│ (API)   │ Service boundaries, DB, LLM mocks
├─────────┤
│ Unit    │ ← 80% of tests, fastest feedback
│ (unittest) Pure functions, business logic,
│         │ state transitions, utilities
└─────────┘
```

### 7.2 Coverage Targets

| Layer | Target | Enforcement |
|-------|--------|-------------|
| Unit (business logic) | 90% | CI gate — PR blocked if <90% |
| Unit (UI components) | 70% | CI warning if <70% |
| Integration (API) | 80% | CI gate — PR blocked if <80% |
| E2E (critical paths) | 100% of P0 flows | CI gate — nightly + pre-release |

### 7.3 Current Test Coverage

| Test Module | Tests | Status |
|-------------|-------|--------|
| `test_stage9_libraries` | 15+ | Passing |
| `test_integration_smoke` | 8+ | Passing (3 credential-gated skips expected) |
| `test_telegram` | 5+ | Passing |
| `test_intent_parser` | 5+ | Passing |
| `test_github` | 3+ | Passing |
| `test_autopilot` | 34 | Passing |
| `test_vector_search` | 5+ | Passing |
| `test_dashboard_api` | 5+ | Passing |
| **Total** | **59+** | **All passing** |

### 7.4 Mocking Strategy

| Dependency | Mock Tool | Strategy |
|------------|-----------|----------|
| LLM APIs (Gemini) | `unittest.mock.patch` | Return deterministic responses for test fixtures. Never hit real APIs in unit tests. |
| OAuth Providers | `unittest.mock.patch` | Mock token exchange endpoints. Pre-canned token responses. |
| PostgreSQL | testcontainers or in-memory | Real DB for integration tests; mock for unit tests. |
| Vector DB | In-memory HNSW | Lightweight in-memory vector index for deduplication tests. |
| n8n API | `unittest.mock.patch` | Mock httpx.Client for n8n REST API calls. |

### 7.5 Critical User Journeys (CUJs)

| CUJ ID | Journey | Priority | Test Tool |
|--------|---------|----------|-----------|
| CUJ-001 | Sign up → Connect Gmail → View First Digest | P0 | Playwright |
| CUJ-002 | Receive email → Approve smart draft → Send → Verify sent | P0 | Playwright + API verification |
| CUJ-003 | Add library entry → Search → Verify vector match | P1 | Playwright |
| CUJ-004 | Panic button (soft) → Verify data preserved → Reconnect | P1 | Playwright |
| CUJ-005 | Create goal → Add tasks → Complete tasks → Verify progress | P1 | Playwright |
| CUJ-006 | YOLO Mode: Inject custom LLM key → Run workflow → Verify cost attribution | P2 | Playwright |

### 7.6 Performance Budgets

| Metric | Budget | Enforcement |
|--------|--------|-------------|
| First Contentful Paint (FCP) | < 1.2s | Lighthouse CI gate |
| Largest Contentful Paint (LCP) | < 2.5s | Lighthouse CI gate |
| Time to Interactive (TTI) | < 3.5s | Lighthouse CI gate |
| Total Blocking Time (TBT) | < 200ms | Lighthouse CI gate |
| Cumulative Layout Shift (CLS) | < 0.1 | Lighthouse CI gate |
| Bundle size (initial) | < 200KB gzipped | Bundle analyzer gate |

---

## 8. Resilience, Error Mitigation & Observability

### 8.1 Error Handling Strategy

#### Current Implementation

- **Integration Errors:** Each integration client catches `httpx.HTTPStatusError` separately, logs with `logger.exception()`, and raises.
- **Command Errors:** `route_command()` catches all exceptions, logs, and returns a user-friendly reply string.
- **Autopilot Errors:** Governor blocks dangerous operations. Tool execution failures are recorded as observations and the task pauses.

#### Target Implementation (v1.0)

- **Error Abstraction Layer (INFRA-05):** Translates technical n8n/backend errors into soft, actionable AI-Guide messages. Error classification enum: `CREDENTIAL_EXPIRED`, `CREDENTIAL_REVOKED`, `INTEGRATION_NOT_CONNECTED`, `N8N_UNREACHABLE`, `WORKFLOW_NOT_FOUND`, `RATE_LIMITED`, `UNKNOWN`.
- **Soft Error Messages:** Plain language, no stack traces. Example: "That didn't work — your Gmail connection may have expired. Reconnect?"
- **One Automatic Retry:** On failure, retry once before bothering the owner (D-10). If retry also fails, surface soft message.

### 8.2 Circuit Breakers

| Resource | Threshold | Action |
|----------|-----------|--------|
| LLM API | p95 > 10s for 5 minutes | Auto-fallback to backup provider |
| n8n API | 3 consecutive failures | Pause workflow execution, notify owner |
| OAuth Token Refresh | > 10 users affected | Batch notification to affected users |
| Database Connection Pool | > 90% for 3 minutes | Auto-scale connection pool + page DBA |

### 8.3 Alerting Rules

| Alert | Condition | Severity | Response |
|-------|-----------|----------|----------|
| API Down | Error rate > 1% for 2 minutes | P1 | Auto-page on-call |
| LLM Latency Spike | p95 > 10s for 5 minutes | P2 | Slack alert + auto-fallback |
| OAuth Token Refresh Fail | > 10 users | P2 | Slack alert + user notification batch |
| DB Connection Pool Exhausted | > 90% for 3 minutes | P1 | Auto-scale + page DBA |
| n8n RCE Detected | Security alert triggered | P0 | Immediate incident commander + auto-isolate pod |
| Cost Anomaly | Daily LLM spend > 150% of 7-day avg | P2 | Slack alert + billing freeze for flagged accounts |

### 8.4 Observability

- **Structured Logging:** JSON format with correlation IDs. 100% for errors, 10% for success (configurable).
- **Distributed Tracing:** OpenTelemetry for request flow across services.
- **Metrics:** Prometheus for system metrics (request rate, error rate, latency percentiles).
- **Health Endpoints:** `/healthz` for liveness, `/api/v1/dashboard/health` for integration status.

---

## 9. User Flow Architecture & State Machines

### 9.1 Onboarding Flow (State Machine)

```
[ENTRY] → [AUTH_PENDING]
    │
    │ OAuth success
    ▼
[IDENTITY_CAPTURE]
    │
    │ User submits Identity Box
    │ System: NLP parse → persona tag → template selection
    ▼
[PERSONA_ASSIGNED]
    │
    │ System: Suggest integrations (progressive auth)
    ▼
[INTEGRATION_AUTH_1] (e.g., Gmail)
    │
    │ Auth success OR skip
    ▼
[INTEGRATION_TEST_1]
    │
    │ Connection valid?
    │ YES → [INTEGRATION_AUTH_2] (optional)
    │ NO → [INTEGRATION_RETRY_1] (max 3 attempts)
    ▼
[DATA_FETCH]
    │
    │ System: Fetch last 24h data from connected sources
    │ Timeout: 45 seconds max
    ▼
[DIGEST_GENERATION]
    │
    │ LLM processing + deduplication
    │ Fallback: Show raw data if LLM fails
    ▼
[FIRST_DIGEST_READY]
    │
    │ Display digest inline (the "Instant Win")
    ▼
[TOMORROW_PREVIEW]
    │
    │ System: "Tomorrow at 6 AM, I'll deliver your Morning Brief..."
    ▼
[ONBOARDING_COMPLETE]
    │
    │ Redirect to Dashboard
    ▼
[DASHBOARD_ACTIVE]
```

**Edge Cases:**
- `[AUTH_PENDING]` → timeout 10min → show "Having trouble? Use email magic link instead"
- `[IDENTITY_CAPTURE]` → empty input → allow skip, assign "General Professional" persona
- `[INTEGRATION_AUTH_1]` → user declines all → enter "Manual Mode" (no integrations, library-only)
- `[DATA_FETCH]` → timeout 45s → show partial data + "Still catching up on the rest..."
- `[DIGEST_GENERATION]` → LLM failure → show raw email subjects + "I need a moment to summarize these"

### 9.2 Core Dashboard State Machine

```
[DASHBOARD_ACTIVE]
│
├──► [VIEW_DASHBOARD] (default)
│    │
│    ├──► [CRITICAL_FOCUS_EXPANDED] (click task card)
│    │    │
│    │    ├──► [TASK_ACTION_SELECTED] (approve, defer, delegate)
│    │    │    │
│    │    │    ├──► [TASK_COMPLETED] → update state, animate out
│    │    │    ├──► [TASK_DEFERRED] → move to "Tomorrow" queue
│    │    │    └──► [TASK_DELEGATED] → open draft composer
│    │    │
│    │    └──► [VIEW_DASHBOARD] (close card)
│    │
│    ├──► [CONTEXT_NEST_CARD_EXPANDED]
│    │    │
│    │    ├──► [CARD_ACTION_REPLY] → open AI Guide with draft context
│    │    ├──► [CARD_ACTION_SAVE] → add to Library
│    │    ├──► [CARD_ACTION_DISMISS] → remove, learn preference
│    │    └──► [CARD_ACTION_SHARE] → generate shareable link
│    │
│    └──► [AI_GUIDE_COMMAND] (user types in command bar)
│         │
│         ├──► [COMMAND_RECOGNIZED] → execute, show result
│         ├──► [COMMAND_AMBIGUOUS] → ask clarifying question
│         └──► [COMMAND_UNKNOWN] → suggest similar commands
│
├──► [VIEW_LIBRARY]
│    │
│    ├──► [SEARCH_ACTIVE] (user types in search bar)
│    │    │
│    │    ├──► [SEARCH_RESULTS] (vector + keyword matches)
│    │    └──► [SEARCH_NO_RESULTS] → suggest related terms
│    │
│    └──► [ENTRY_OPENED] → full content view
│
├──► [VIEW_PLANNER]
│    │
│    ├──► [TASK_SELECTED] → edit status, priority, due date
│    ├──► [HABIT_CHECKIN] → toggle today's check-in
│    └──► [GOAL_EXPANDED] → view progress, child tasks
│
└──► [SETTINGS_OPENED]
     │
     ├──► [PROFILE_TAB] → edit identity, persona
     ├──► [INTEGRATIONS_TAB] → add/remove connections
     ├──► [PRIVACY_TAB] → export, delete, consent management
     └──► [NOTIFICATIONS_TAB] → digest schedule, quiet hours
```

**Global States (available from any view):**
- `[PARK_DISTRACTION]` → quick capture modal → dumps to inbox → AI Guide acknowledges
- `[PANIC_BUTTON_SOFT]` → confirmation modal → flush cache, reset AI context
- `[PANIC_BUTTON_HARD]` → multi-step confirmation + export offer → full wipe
- `[HELP_OVERLAY]` → contextual tips based on current view

### 9.3 Digest Generation Flow (Backend)

```
[TRIGGER: Scheduled (6 AM user TZ) OR Manual Refresh]
    │
    ▼
[COLLECT_SOURCES]
    │
    ├──► Gmail API (last 24h, unread + flagged, max 50)
    ├──► RSS Feeds (last 24h, new items, max 20 per feed)
    └──► Calendar (next 24h events, action items from last meeting)
    │
    ▼
[FILTER_NOISE]
    │
    ├──► Spam detection (trained model + user history)
    ├──► Newsletter categorization (auto-archive if user consistently dismisses)
    ├──► Priority scoring (Critical Focus Block ranking)
    └──► Deduplication (vector similarity > 0.85 → merge)
    │
    ▼
[PII_REDACTION]
    │
    ├──► Regex: emails, phones, SSNs, credit cards
    ├──► NER: names, addresses, companies
    └──► Replace with tokens: [EMAIL_1], [PERSON_1], [COMPANY_1]
    │
    ▼
[LLM_SUMMARIZATION]
    │
    ├──► Batch items by source (emails batch, news batch, etc.)
    ├──► Construct prompt with user persona + style preferences
    ├──► Call LLM (with circuit breaker + fallback)
    ├──► Parse structured output (JSON schema enforced)
    └──► Validate: 3 bullets max, 1 sentence each, reading time < 2 min
    │
    ▼
[QUALITY_GATE]
    │
    ├──► Hallucination check: factual consistency with source
    ├──► Tone check: matches user style profile
    ├──► Length check: within bounds
    └──► If fail: retry once with stricter prompt, then fallback to raw excerpt
    │
    ▼
[ASSEMBLE_DIGEST]
    │
    ├──► Critical Focus Block (top 3–5 scored items)
    ├──► Context Nest (remaining items by source, 3 bullets each)
    ├──► Action Required chips (reply, schedule, approve, review)
    └──► "Tomorrow Preview" (what Signal will watch for)
    │
    ▼
[DELIVER]
    │
    ├──► In-app notification (real-time WebSocket push)
    ├──► Email backup (if user hasn't opened app in 2 hours)
    └──► Mobile push (if enabled, quiet hours respected)
```

### 9.4 Smart Draft Flow

```
[USER: Clicks "Draft Reply" on email card OR types command in AI Guide]
    │
    ▼
[CONTEXT_GATHERING]
    │
    ├──► Fetch email thread (full history, last 10 messages)
    ├──► Fetch user style profile (last 10 sent emails, tone analysis)
    ├──► Fetch relationship context (last interaction date, topic history)
    └──► Fetch calendar (availability for proposed meeting times)
    │
    ▼
[INTENT_CLASSIFICATION]
    │
    ├──► Reply type: acceptance, rejection, deferral, question, information
    ├──► Urgency: high (same day), medium (this week), low (whenever)
    └──► Tone target: friendly, firm, apologetic, excited, neutral
    │
    ▼
[DRAFT_GENERATION]
    │
    ├──► Construct prompt with all context + constraints
    ├──► LLM call (primary provider, 10s timeout)
    ├──► Parse output: subject line, body, suggested send time
    └──► Quality check: no hallucinations, appropriate tone, correct facts
    │
    ▼
[PRESENT_TO_USER]
    │
    ├──► Show draft in AI Guide panel with diff highlighting
    ├──► Offer tone variants: [Approve] [Friendlier] [Firmer] [Shorter] [Longer]
    └──► Show confidence score: "I'm 94% confident this captures your style"
    │
    ▼
[USER_ACTION]
    │
    ├──► [APPROVE_AND_SEND] → Send via Gmail API → Log to audit
    ├──► [EDIT_AND_SEND] → Open inline editor → User edits → Send
    ├──► [SCHEDULE_SEND] → Queue for optimal time → Calendar check → Send later
    ├──► [SAVE_DRAFT] → Store in Library → Tag: "Drafts pending"
    └──► [DISMISS] → Log rejection reason → Update style model
```

### 9.5 Edge Case Catalog

| Scenario | System Behavior | User Experience |
|----------|----------------|-----------------|
| User has zero emails in 24h | Skip email section, show "No new emails" with celebration animation | "You're entirely caught up." |
| LLM returns malformed JSON | Retry once with stricter schema prompt. If still bad, fallback to raw excerpt | Card shows raw subject + "I couldn't summarize this one neatly." |
| OAuth token revoked by user externally | Detect on next API call (401). Auto-trigger re-auth flow. | Banner: "Gmail needs reconnecting. Tap here." |
| Two emails are 90% similar | Deduplicate into single card with "+1 similar" badge | Single card: "2 emails about project deadline" |
| User types gibberish in command bar | Intent classification fails. Suggest 3 most likely commands. | "Did you mean: 'Draft reply to Joe' or 'Summarize last meeting'?" |
| n8n workflow enters infinite loop | Execution timeout (30s). Circuit breaker opens. Kill container. | "This automation took too long. I've paused it for your safety." |
| User has 200+ unread emails | Process top 50 by priority. Queue rest for next digest. | "I prioritized the 50 most important emails. The rest are in your queue." |

---

## 10. UI/UX Design System & Interaction Patterns

### 10.1 Design Philosophy: "Digital Minimalism"

**Core Principles:**
1. **Cognitive Load Budget:** Every screen element must earn its place. If it doesn't reduce decisions or provide clarity, remove it.
2. **Progressive Disclosure:** Show the minimum viable information. Reveal depth only on intent (hover, click, expand).
3. **Calm Technology:** No blinking, no bouncing, no red alerts. Status changes are subtle (color shifts, gentle fade-ins).
4. **Friction by Design:** Destructive actions (send, delete, reset) require intentional confirmation. Helpful actions (save, draft) are one-tap.

### 10.2 Design Tokens

#### Color Palette

```css
:root {
  /* Base */
  --color-bg-primary: #FAFAF8;      /* Warm off-white — paper-like calm */
  --color-bg-secondary: #F5F5F0;    /* Slightly darker for cards/panels */
  --color-bg-tertiary: #EBEBE5;     /* Borders, dividers */
  --color-bg-inverse: #1A1A1A;      /* Dark mode primary */

  /* Text */
  --color-text-primary: #1A1A1A;    /* High contrast for reading */
  --color-text-secondary: #6B6B6B;  /* Metadata, timestamps */
  --color-text-tertiary: #9E9E9E;   /* Disabled, hints */
  --color-text-inverse: #FAFAF8;    /* On dark backgrounds */

  /* Accent — Single accent color system */
  --color-accent: #2D6A4F;          /* Deep forest green — growth, calm, action */
  --color-accent-light: #40916C;    /* Hover states */
  --color-accent-dark: #1B4332;     /* Active states */
  --color-accent-muted: #D8F3DC;    /* Backgrounds for accent-related items */

  /* Semantic */
  --color-success: #2D6A4F;         /* Same as accent — positive is the default */
  --color-warning: #D4A373;         /* Warm amber — gentle attention */
  --color-error: #C75146;           /* Muted red — serious but not alarming */
  --color-info: #74C69D;            /* Light green — neutral information */
}
```

**Color Usage Rules:**
- Never use pure black (#000000) or pure white (#FFFFFF). Always use the warm off-whites and soft blacks above.
- Accent color is used sparingly: Primary buttons, active states, progress indicators, and the "Approve" action.
- Error red is never used for non-critical states. A failed draft uses the warning amber, not red.

#### Typography

```css
:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', monospace;

  /* Scale — Major Third (1.25) ratio, base 16px */
  --text-xs: 0.75rem;     /* 12px — captions, badges */
  --text-sm: 0.875rem;    /* 14px — secondary text, metadata */
  --text-base: 1rem;      /* 16px — body, cards */
  --text-lg: 1.25rem;     /* 20px — subheadings, command bar */
  --text-xl: 1.5rem;      /* 24px — section headers */
  --text-2xl: 1.875rem;   /* 30px — page titles */
  --text-3xl: 2.25rem;    /* 36px — hero, onboarding headlines */
}
```

**Typography Rules:**
- Maximum 2 font weights per screen. Usually 400 (body) + 600 (headings).
- Card titles: 16px semibold, 1.25 line height, max 2 lines (truncate with ellipsis).
- Bullet points: 14px normal, 1.5 line height, max 1 line per bullet (strictly enforced).

#### Spacing & Layout

```css
:root {
  /* 4px base grid */
  --space-1: 0.25rem;   /* 4px — icon padding */
  --space-2: 0.5rem;    /* 8px — tight gaps */
  --space-3: 0.75rem;   /* 12px — card internal padding */
  --space-4: 1rem;      /* 16px — standard gap */
  --space-6: 1.5rem;    /* 24px — card external margin */
  --space-8: 2rem;      /* 32px — panel padding */

  /* Border Radius */
  --radius-sm: 4px;     /* Buttons, badges */
  --radius-md: 8px;     /* Cards, inputs */
  --radius-lg: 12px;    /* Modals, panels */
  --radius-full: 9999px;/* Pills, avatars */

  /* Shadows — Subtle, never harsh */
  --shadow-sm: 0 1px 2px rgba(26, 26, 26, 0.04);
  --shadow-md: 0 4px 12px rgba(26, 26, 26, 0.06);
  --shadow-lg: 0 8px 24px rgba(26, 26, 26, 0.08);
  --shadow-focus: 0 0 0 3px rgba(45, 106, 79, 0.15); /* Accent ring */
}
```

#### Motion & Animation

```css
:root {
  --duration-instant: 100ms;  /* Hover states, color changes */
  --duration-fast: 200ms;     /* Button presses, toggles */
  --duration-normal: 300ms;   /* Card transitions, panel slides */
  --duration-slow: 500ms;     /* Page transitions, modal entrances */

  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-decelerate: cubic-bezier(0, 0, 0.2, 1);
  --ease-accelerate: cubic-bezier(0.4, 1, 1, 1);
}
```

**Animation Rules:**
- No animation > 500ms. User attention is precious.
- Respect `prefers-reduced-motion`: All animations degrade to instant transitions.
- Purposeful motion only: Elements move to show relationship (hierarchy, causality), never for decoration.
- Loading states: Never use spinners for > 500ms. Use skeleton screens or progressive text reveal.

### 10.3 Component Library

#### Card (Context Nest)

```
┌─────────────────────────────────────────┐
│ [icon] Source Name [time] 2h            │ ← 12px secondary, top row
│                                         │
│ • First bullet point here, one line max │ ← 14px normal, bullet list
│ • Second bullet point, also one line    │
│ • Third bullet point, final summary     │
│                                         │
│ [Reply] [Save] [Dismiss]               │ ← Action chips, 12px medium
└─────────────────────────────────────────┘
```

**Specs:**
- Background: `--color-bg-secondary`
- Border: 1px solid `--color-bg-tertiary`
- Border-radius: `--radius-md` (8px)
- Padding: `--space-3` (12px)
- Max-height: 140px (enforces 3-bullet constraint)
- Hover: shadow-md transition, 200ms

#### Critical Focus Block

```
┌─────────────────────────────────────────┐
│ Critical Focus [3 of 5]                 │ ← Accent color top border (2px)
│ ───────────────────────────────────── │
│                                         │
│ [1] Reply to Client about contract      │ ← Numbered, 16px semibold
│ Due: Today • From: Gmail                │ ← 12px secondary metadata
│ [Draft Reply] [Defer to Tomorrow]       │ ← Primary + secondary buttons
│                                         │
│ [2] Review Q3 budget proposal           │
│ Due: Tomorrow • From: Slack             │
│ [Open] [Remind me at 3pm]              │
└─────────────────────────────────────────┘
```

**Specs:**
- Top border: 2px solid `--color-accent`
- Background: `--color-bg-primary`
- Numbering: 20px semibold, accent color, circular background
- Empty state: Centered illustration + "You are entirely caught up." + subtle confetti animation

#### AI Guide Panel (Right 30%)

```
┌─────────────────────────────────────────┐
│ Signal Guide                            │ ← Sticky header, 16px semibold
│ ───────────────────────────────────── │
│                                         │
│ Status: "I processed 142 items of       │ ← 14px secondary
│ noise for you today. Relax."            │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ Contextual Actions:              │    │ ← Dynamic button row
│ │ [Draft Reply] [Schedule] [Save]  │    │
│ └─────────────────────────────────┘    │
│                                         │
│ ─── Chat History ───                   │
│ Guide: "I noticed 3 emails from         │ ← 14px normal, max 50 messages
│ clients waiting. Want me to draft       │
│ responses?"                             │
│                                         │
│ User: "Draft friendly reply to Joe      │
│ saying Thursday works"                  │
│                                         │
│ Guide: "Done. Here's the draft:         │
│ [preview card] [Approve] [Edit]"        │
│                                         │
│ ───────────────────────────────────── │
│ [Park a Distraction]                    │ ← Quick action, always visible
│ ┌─────────────────────────────────┐    │
│ │ Type a command...                │    │ ← Input field, 16px medium
│ └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

**Specs:**
- Width: 30% desktop, min 320px, max 400px
- Background: `--color-bg-secondary`
- Border-left: 1px solid `--color-bg-tertiary`
- Height: 100vh, sticky position
- Chat bubbles: User right-aligned (accent-muted bg), Guide left-aligned (bg-primary)
- Input: Fixed bottom, auto-resize textarea (max 5 lines)

#### Command Bar

**Input States:**
- **Empty:** Placeholder "Type a command or ask me anything..."
- **Typing:** Real-time intent suggestion dropdown (max 5 suggestions)
- **Recognized:** Green left border + "I'll draft a reply to Joe"
- **Ambiguous:** Yellow left border + "Did you mean reply to Joe or schedule with Joe?"
- **Unknown:** Red left border + "I'm not sure. Try: 'Draft reply to [name]'"

**Autocomplete Triggers:**
- `/` prefix for slash commands (e.g., `/draft`, `/schedule`, `/search`)
- `@` prefix for mentioning contacts (pulls from relationship graph)
- `#` prefix for tags (pulls from Library tags)

### 10.4 Mobile-First Layout (Telegram Mini App)

The primary surface is a Telegram Mini App. The layout adapts:

```
┌─────────────────────────────────┐
│ Signal                    [≡]   │ ← Header with menu
├─────────────────────────────────┤
│                                 │
│  ┌───────────────────────────┐ │
│  │ Critical Focus            │ │ ← Swipeable cards
│  │ [1] Reply to Client...   │ │
│  │ [Draft Reply] [Defer]    │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ Context Nest              │ │ ← Scrollable grid
│  │ [Email] [News] [Chat]    │ │
│  └───────────────────────────┘ │
│                                 │
├─────────────────────────────────┤
│ [Home] [Library] [Plan] [Chat] │ ← Bottom nav
└─────────────────────────────────┘
```

**Mobile-Specific Rules:**
- Bottom navigation with 4 primary tabs + "More" drawer
- Pull-to-refresh on all list views
- Swipe gestures for card actions (left = dismiss, right = save)
- Haptic feedback on action confirmations
- Safe area insets for notch/home indicator

---

## 11. API Contract

### 11.1 Base Configuration

- **Base URL:** `import.meta.env.VITE_API_BASE` (local: `http://localhost:8000`, prod: `https://api.apsmono.com`)
- **Auth:** Firebase ID token as `Authorization: Bearer <token>` header on all `/api/v1/*` endpoints
- **Public Endpoints:** `/healthz`, `/command` require no auth

### 11.2 Current Endpoints

| Method | Path | Purpose | Dashboard View |
|--------|------|---------|----------------|
| GET | `/healthz` | Server health | — |
| POST | `/command` | Send text command | Send Command |
| GET | `/api/v1/dashboard/stats` | Library counts + integration health | Overview |
| GET | `/api/v1/dashboard/health` | Integration health check | Overview |
| GET | `/api/v1/commands` | Recent command history | Commands |
| GET | `/api/v1/reminders` | Pending reminders | Reminders |
| POST | `/api/v1/reminders` | Create reminder | Reminders |
| DELETE | `/api/v1/reminders/{id}` | Delete reminder | Reminders |
| GET | `/api/v1/library/entries` | Browse/filter entries | Library |
| GET | `/api/v1/library/entries/{id}` | Read single entry | Library (modal) |
| PUT | `/api/v1/library/entries/{id}` | Update entry content | Library (edit) |
| POST | `/api/v1/library/entries/{id}/synthesize` | AI Q&A on single entry | Library (AI tab) |
| GET | `/api/v1/library/sections` | List sections | Library (filter) |
| GET | `/api/v1/library/tags` | List all tags | Library (filter) |
| POST | `/api/v1/library/youtube-transcript` | Fetch YouTube transcript | Link Capture |
| GET | `/api/v1/library/graph` | Nodes + edges for graph | Graph |
| GET | `/api/v1/library/timeline` | Chronological stream | Timeline |
| GET | `/api/v1/analysis/tags` | Tag frequencies, trending, orphans | Analysis |
| GET | `/api/v1/analysis/gaps` | Empty sections, stale entries | Analysis |
| GET | `/api/v1/analysis/activity` | Daily counts, velocity | Analysis |
| POST | `/api/v1/analysis/synthesize` | AI synthesis across entries | Analysis |
| GET | `/api/v1/planning/goals` | Active/paused/completed goals | Planning |
| GET | `/api/v1/planning/projects` | Active/completed projects | Planning |
| GET | `/api/v1/planning/reviews` | Weekly/monthly reviews | Planning |
| POST | `/api/v1/planning/review` | Generate AI weekly review | Planning |
| GET | `/api/v1/planning/focus` | AI-suggested priorities | Planning |
| GET | `/api/v1/planning/tasks` | List tasks | Planning |
| POST | `/api/v1/planning/tasks` | Create task | Planning |
| PUT | `/api/v1/planning/tasks/{id}` | Update task | Planning |
| DELETE | `/api/v1/planning/tasks/{id}` | Delete task | Planning |
| GET | `/api/v1/planning/habits` | List habits | Planning |
| POST | `/api/v1/planning/habits` | Create habit | Planning |
| PUT | `/api/v1/planning/habits/{id}/checkin` | Check in habit | Planning |
| PUT | `/api/v1/planning/habits/{id}/uncheckin` | Undo check-in | Planning |
| DELETE | `/api/v1/planning/habits/{id}` | Delete habit | Planning |
| POST | `/api/v1/guide/command` | AI Guide command | AI Guide |
| GET | `/api/v1/guide/status` | Guide metrics | AI Guide |
| POST | `/api/v1/guide/park` | Park a distraction | AI Guide |
| POST | `/api/v1/autopilot/tasks` | Start autopilot task | Autopilot |
| GET | `/api/v1/autopilot/tasks` | List autopilot tasks | Autopilot |
| POST | `/api/v1/autopilot/tasks/{id}/approve` | Approve task | Autopilot |
| GET | `/api/v1/autopilot/approvals` | List approvals | Autopilot |

### 11.3 Planned Endpoints (v1.0)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/n8n/execute` | Trigger n8n workflow |
| GET | `/api/v1/n8n/executions` | List execution history |
| GET | `/api/v1/n8n/executions/{id}` | Get execution status |
| POST | `/webhook/n8n` | n8n execution callback |
| GET | `/api/v1/feeds` | List feed subscriptions |
| POST | `/api/v1/feeds` | Add feed subscription |
| GET | `/api/v1/feeds/items` | Get feed items |
| POST | `/api/v1/drafts/generate` | Generate smart draft |
| PUT | `/api/v1/drafts/{id}/approve` | Approve and send draft |
| GET | `/api/v1/user/data-export` | Export user data (GDPR) |
| DELETE | `/api/v1/user/delete` | Delete user account (GDPR) |

### 11.4 Error Responses

All endpoints return standard HTTP status codes:
- `401` — Missing or invalid Bearer token
- `404` — Entry not found (library endpoints)
- `429` — Rate limit exceeded
- `200` with `{"status": "error", "reply": "..."}` — Business logic error

---

## 12. Monetization & Subscription Strategy

### 12.1 Pricing Matrix

| Subscription Tier | Pricing | Core Usage Limits | Key Features |
|-------------------|---------|-------------------|--------------|
| **7-Day "Aha!" Trial** | $0 | Full Access for 7 Days | Guided Onboarding, App integrations, Live 24hr Mini-Digest testing |
| **The Calm Tier** | $39/mo | 1,000 processed items/mo, 500 library items saved, Max 10 smart feeds | Full Zen Dashboard, AI Guide, Routine Planner, Pre-verified n8n templates |
| **The YOLO / Power Tier** | $99/mo | 10,000 processed items/mo, 5,000 library items saved, Uncapped executions | Full Advanced Developer Sandbox, Raw JSON editing, Custom LLM key injection, Priority execution queues |

### 12.2 Usage Metering

| Metric | What Counts | Free Limit | Pro Limit | Business Limit |
|--------|-------------|------------|-----------|----------------|
| Items Processed | Emails summarized, news items deduplicated, feed items compressed | 100/mo | 1,000/mo | 10,000/mo |
| Library Items | Total entries in knowledge library | 50 | 500 | 5,000 |
| Smart Drafts | Draft replies generated | 10/mo | 100/mo | 1,000/mo |
| Feed Subscriptions | Active RSS/news feeds | 3 | 10 | 50 |
| Autopilot Tasks | Autonomous task executions | 5/mo | 50/mo | 500/mo |

### 12.3 Billing Integration

- **Provider:** Stripe
- **Flow:** Upgrade prompt in Settings → Stripe Checkout → Webhook confirms → Feature unlock
- **Grace Period:** 7 days after payment failure before downgrade
- **Annual Discount:** 20% off ($31/mo Pro, $79/mo Business)

---

## 13. Implementation Roadmap

### Phase 1: Data & Auth Foundation (COMPLETE)

**Goal:** Establish the data spine and authentication foundation.

- [x] PostgreSQL + pgvector vector database
- [x] Gemini embedding client (768-dim)
- [x] Hybrid search (keyword + vector)
- [x] Firebase session cookie auth
- [x] Library entry auto-indexing
- [x] Token cache for embedding reuse

### Phase 2: n8n Execution Layer (IN PROGRESS)

**Goal:** Wire the brain to n8n as the firm execution engine.

- [ ] n8n REST API thin client (`src/n8n/client.py`)
- [ ] Credential injection (`src/n8n/credentials.py`)
- [ ] Template skeleton loader (`src/n8n/templates.py`)
- [ ] Intent → template → execution orchestrator (`src/n8n/executor.py`)
- [ ] Error abstraction layer (`src/n8n/errors.py`)
- [ ] Webhook callback endpoint (`src/api/n8n_callback.py`)
- [ ] RL approval gate for side-effecting workflows
- [ ] Unit tests (`tests/test_n8n_execution.py`)

### Phase 3: Knowledge Library + Conceptual Search + AI Guide

**Goal:** Transform the library from file-based to AI-powered knowledge system.

- [ ] Enhanced vector search with re-ranking
- [ ] AI Guide conversational interface
- [ ] Contextual action suggestions
- [ ] Library entry synthesis improvements
- [ ] Graph visualization enhancements

### Phase 4: Telegram Mini App

**Goal:** Make Signal available as a Telegram Mini App.

- [ ] Telegram Mini App frontend (React + Telegram WebApp API)
- [ ] Mobile-optimized layout (bottom nav, swipe gestures)
- [ ] Telegram-specific auth flow (Telegram Login Widget → Firebase custom token)
- [ ] Push notifications via Telegram bot
- [ ] Inline keyboard for quick actions

### Phase 5: Digest Engine

**Goal:** Automated daily digest generation and delivery.

- [ ] Gmail inbox summarization (last 24h)
- [ ] Priority scoring algorithm
- [ ] PII redaction pipeline
- [ ] LLM summarization with quality gate
- [ ] Digest assembly (Critical Focus Block + Context Nest)
- [ ] Scheduled delivery (APScheduler)
- [ ] Engagement tracking

### Phase 6: Smart Feeds

**Goal:** Noise-free content consumption.

- [ ] YouTube transcript abstraction
- [ ] RSS feed subscription management
- [ ] News deduplication (vector similarity)
- [ ] Feed item compression (3-bullet cards)
- [ ] Silent queueing for reading routines

### Phase 7: Smart Drafts

**Goal:** Context-aware reply generation.

- [ ] Email thread context gathering
- [ ] User style profile analysis
- [ ] Relationship context integration
- [ ] Draft generation with tone variants
- [ ] One-click approve & send
- [ ] Draft scheduling

### Phase 8: Polish & Launch

**Goal:** Production hardening and public launch.

- [ ] Security audit (STRIDE review)
- [ ] Performance testing (k6 load tests)
- [ ] E2E test suite (Playwright)
- [ ] Error monitoring (Sentry or similar)
- [ ] Status page (status.signal.app)
- [ ] Landing page
- [ ] Billing integration (Stripe)
- [ ] GDPR compliance (data export, deletion)

---

## 14. Decision Log & Risk Matrix

### 14.1 Architecture Decision Log

| ID | Date | Decision | Context | Status |
|----|------|----------|---------|--------|
| ADL-001 | 2026-05 | Use n8n as optional backend, not sole dependency | Licensing risk, multi-tenancy gaps | Pending — requires n8n enterprise license negotiation |
| ADL-002 | 2026-05 | Signal-native workflow schema | Decouple from n8n JSON, enable provider switching | Approved |
| ADL-003 | 2026-05 | Token Vault with zero-knowledge proxy | Security, compliance, user trust | Approved — custom build for cost control |
| ADL-004 | 2026-05 | Anthropic Claude as default LLM | Stronger privacy posture (no training by default) | Approved — with OpenAI fallback for vision tasks |
| ADL-005 | 2026-05 | Freemium model (Free/Pro/Business/YOLO) | Market anchor at $20, conversion optimization | Approved — replaces original trial model |
| ADL-006 | 2026-05 | React + TypeScript frontend | Team expertise, ecosystem, performance | Approved |
| ADL-007 | 2026-05 | PostgreSQL + Redis + Vector DB (pgvector) | Relational data, caching, semantic search | Approved |
| ADL-008 | 2026-05 | Gemini as primary AI provider | Cost, speed, Indonesian language support | Approved — decision record 006 |

### 14.2 Risk Matrix

| Risk | Likelihood (1-5) | Impact (1-5) | Risk Score | Mitigation | Owner | Status |
|------|-------------------|--------------|------------|------------|-------|--------|
| n8n license revocation | 3 | 5 | 15 | Signal-native schema decouples from n8n | CTO/Legal | Active |
| n8n critical security vulnerability | 4 | 5 | 20 | Sandbox isolation, WAF rules | Security Lead | Active |
| LLM API cost spike | 3 | 4 | 12 | Caching layer, cost caps per tier | Engineering Lead | Active |
| User data privacy breach | 2 | 5 | 10 | Encryption, ZDR, SOC 2 roadmap | Security Lead | Active |
| Competitor launches "Zen" product | 3 | 3 | 9 | Speed to market critical | Product Lead | Monitoring |
| YOLO Mode RCE via user code | 4 | 5 | 20 | gVisor sandbox, AST analysis | Security Lead | Active |
| OAuth provider API changes | 3 | 3 | 9 | Abstraction layer reduces impact | Engineering Lead | Monitoring |
| LLM output quality degradation | 4 | 3 | 12 | Weekly eval suite, prompt versioning | ML Lead | Active |

---

## 15. Glossary

| Term | Definition |
|------|------------|
| **Brain** | The solo-leveling FastAPI backend — the central command center |
| **Critical Focus Block** | Dashboard panel showing top 3–5 highest-priority actionable items |
| **Context Nest** | Grid of cards containing compressed data streams (emails, news, chats) |
| **Deep Capture** | AI-assisted "add to library" flow that creates research bundles |
| **Digest** | Daily summary of processed items, delivered via app/email/push |
| **Governor** | RL-based safety gate that controls AI autonomy levels |
| **Identity Box** | Onboarding input field for user to describe their work and overwhelm |
| **Instant Win** | First live digest generated during onboarding to prove immediate value |
| **Intent Map** | Keyword-to-handler mapping in router.py |
| **Library** | File-based knowledge store under `library/` with markdown entries |
| **n8n** | Workflow automation engine used as the execution backend |
| **Park a Distraction** | Quick-capture feature to offload thoughts without breaking focus |
| **Research Bundle** | A directory of 7 markdown files created during deep capture |
| **RL Level** | Responsibility Level (RL1–RL5) defining AI autonomy |
| **Signal** | The product code name for this personal AI command center |
| **Signal-native schema** | Internal JSON format for workflows, decoupled from backend engine specifics |
| **Smart Draft** | Context-aware, style-matching reply generation |
| **Smart Feed** | Noise-free content subscription with deduplication and compression |
| **Spark Card** | Recently added item in Library |
| **Vector Search** | Semantic search using pgvector with Gemini embeddings |
| **YOLO Mode** | Advanced tier allowing custom LLM keys, raw workflow JSON, and guardrail disabling |
| **Zero-Knowledge Proxy** | Token vault architecture where Signal backend cannot read plaintext API keys |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-30 | Signal Team | Initial comprehensive PRD — merged product blueprint, v2.0 refinement, and current codebase state |

**Next Review Date:** 2026-06-15
**Distribution:** Core team, engineering leads, security auditor
