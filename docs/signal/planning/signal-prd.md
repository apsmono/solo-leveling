# Definitive Product Requirement Document (PRD)

**Project Code Name:** Signal
**Phase:** MVP v1.0 Core Architecture
**Source:** `Let's assemble the final product blueprint. Compi....pdf` (extracted to markdown)

---

## 1. Problem Statement & Market Opportunity

In the hyper-digital era, individuals and professionals suffer from intense **"infobesity"** — an overwhelming daily influx of unstructured data (emails, chats, RSS feeds, market metrics). This triggers cognitive fatigue, severe analysis paralysis, and chronic procrastination.

Existing automation tools fall short because they are either highly technical developer-first canvases (requiring complex logic trees and API configurations) or unpredictable and expensive (such as hiring an unverified virtual assistant).

**The Core Pain Point:** Users spend hours performing low-level cognitive labor — filtering, sorting, and summarizing raw information — leaving them with no energy for high-value strategic execution.

## 2. User Persona: The "High-Output Minimalist"

- **Who they are:** Business owners, freelancers, and high-performing professionals who value their time over money. They are willing to pay a premium subscription to protect their focus.
- **Tech Literacy:** Moderate. They use modern apps daily but demand a "plug-and-play" experience. They want to avoid writing code, managing integrations, or mastering complex prompt engineering.
- **Behavioral Goal:** Survive and thrive in a rapid-pace market by staying cleanly informed, without managing ten different communications tabs.

## 3. User Onboarding Flow (The Guided Experience)

The onboarding is explicitly designed to eliminate setup anxiety, targeting a completion time of **under 2 minutes**. A persistent conversational companion, **The AI Guide**, acts as a personalized concierge.

```
[Sign Up via Google/Apple]
        │
        ▼
[The Guide Appears] ────────► "Tell me about your world..." (Identity Box)
        │
        ▼
[Contextual Connection] ────► Guide suggests connecting specific apps via n8n
        │
        ▼
[The Instant Win] ──────────► AI generates the first live 24-hr mini-digest
```

- **Step 1: The Warm Welcome & Identity Box (0:00 - 0:45)**
  - The user signs up instantly using Google or Apple OAuth (no manual password creation).
  - The Identity Box: A single open-ended input field asking: *"In a few sentences, what do you do, and what is currently overwhelming you the most?"*
  - The System Action: The Guide processes this text instantly to map out the user's custom environment templates.
- **Step 2: Guided Integration (0:45 - 1:30)**
  - The Guide processes the entry and highlights only the required app cards (e.g., *"I see you're managing clients. Let's connect your Gmail and WhatsApp first"*). The user authorizes them securely via native OAuth toggles.
- **Step 3: The First Live Digest (1:30 - 2:00)**
  - The backend immediately processes the last 24 hours of data and displays an organized mini-summary right inside the onboarding window to prove immediate value.

## 4. The "Zen" Interface & Dashboard Layout

The interface uses an **asymmetric split-screen layout** designed to maintain absolute cognitive calm.

### Panel A: The Clarity Board (Left 70% Width)

Shifts context cleanly between three core structural views:

**View 1: The Core Dashboard View**
- **The Critical Focus Block:** Restricted to displaying a maximum of 3 to 5 high-priority, actionable tasks extracted from all data streams. If empty, it displays a calming message: *"You are entirely caught up."*
- **The Context Nest:** A clean grid of cards containing highly compressed data streams (Emails, News, Chats). Every card is strictly limited to 3 single-sentence bullet points.

**View 2: The Knowledge Library View (Folderless Sandbox)**
- A centralized, zero-folder digital archive for articles, personal notes, writings, and documentation.
- **Conceptual Search Bar:** A single plain-text input using vector embeddings. Typing *"How to fix supply line issues"* surfaces documents conceptually tagged with logistics, without requiring exact file-name matches.
- **Recent Spark Cards:** A horizontal row of maximum 3 to 4 cards showing recently dropped inputs (forwarded emails, browser extensions, or WhatsApp clips).
- **Active Context Stacks:** Simple, collapsible list views grouped automatically by the AI based on active macro milestones.

**View 3: The Routine & Milestone Planner View (Flow Over Deadlines)**
- **Today's Rhythm:** A minimalist vertical timeline displaying only 2 or 3 core micro-routine time blocks for the day (e.g., Focus Block, Learning Time, Rest). No granular hourly grid lines.
- **Macro Milestones:** Placed safely at the bottom of the screen to track long-term targets without cluttering the daily focus workspace.

### Panel B: The Persistent AI Guide Workspace (Right 30% Width)

A full-height conversational sidebar that remains locked in place across every single tab.
- **Status Banner:** Displays reassuring metrics (e.g., *"I processed 142 items of noise for you today. Relax."*).
- **Contextual Actions:** Changes its suggested buttons dynamically based on what the user is active on (e.g., offering to draft a reply to an active email card).
- **The Command Bar:** A text input field where the user can execute operations naturally (e.g., *"Draft a friendly response to Joe saying I can only do Thursdays"*). It features a quick **[ Park a Distraction ]** gate to quickly dump random thoughts out of the user's head during active focus routines.

## 5. Feature Ecosystem Specifications

### Pillar 1: Smart Feed Subscriptions (Noise-Free Consumption)
- **YouTube Abstraction:** n8n backend processes pull video transcriptions silently. The internal LLM compresses the transcript into a 3-bullet-point takeaway card with reading time metrics.
- **News Deduplication:** Collates matching events into a single situational update card.
- **Controlled Notification Rules:** Disables push alerts entirely; new content queues up silently for designated reading routines.

### Pillar 2: Core Automation & Shadow Work Execution
- **One-Click Smart Drafts:** Generates context-aware, writing-style matching response drafts to urgent communications before the user checks the screen, offering one-click options (Approve & Send, Make Friendlier, Make Firmer).
- **Keep-In-Touch Pulse:** Monitors relationship logs and proactively drafts relationship maintenance touchpoints for the user to approve and send.
- **Automated Pipeline Routing:** Recognizes administrative inputs (like PDF invoices), extracts metrics, logs them to finance cards silently, and alerts only if variances occur.

### Pillar 3: Advanced Customization ("YOLO Mode")
An advanced control toggle inside the configuration console built specifically for power users, hackers, and custom builders.
- **Custom LLM Injection:** Bypasses native models to let users plug in their own direct OpenAI or Anthropic API keys.
- **Direct Node Canvas / JSON Access:** Exposes the raw n8n workflow JSON strings for manual execution, custom JavaScript node code injection, or custom endpoint hooks.
- **Guardrail Disabling:** Permits full automation dispatch bypassing the default human-in-the-loop review requirement.

## 6. Technical Architecture & Backend Strategy

The architecture avoids heavy custom infrastructure by operating as a sleek **Abstraction Layer** wrapped directly on top of an **n8n backend engine** via the n8n API.

```
[ THE USER UI ] ───► Translates Intent into JSON ───► [ YOUR MIDDLEWARE SAAS ]
(Cards, Chat, Automation Toggles)                              │
                                                               ▼ Triggers API
                                                   [ n8n BACKEND ENGINE ]
                                                   (Executes Node Workflows Safely)
```

**Core Infrastructure Guardrails:**
- **Dynamic Credential Injection:** User OAuth tokens securely map directly into corresponding n8n nodes via backend API requests. The user never handles raw API keys or webhook URLs.
- **Token Caching Layer:** Validates incoming articles against a vector database index. If an article matches an existing record, the system serves the cached summary to eliminate duplicate LLM token consumption.
- **YOLO Mode Cost Shifting:** Activating advanced unvalidated scripts or workflows forces the client to input personal API keys, protecting platform server margins from infinite loops or heavy scraping.
- **Error Abstraction Layer:** Intercepts technical JSON errors thrown by backend nodes and transforms them into soft, reassuring messages delivered by the AI Guide interface.

## 7. Safety, Trust & Recovery Operations

- **Human-In-The-Loop Enforcement:** In standard tier setups, no automated communication can exit the platform without a physical click validation from the user.
- **Zero-Retention Privacy:** Employs zero-data-retention APIs for all language model processing. Personal data is never used to train public models.
- **Layout & Memory Reset:** A setting shortcut that flushes active workspace cache and AI Guide conversational loops while keeping connected app tokens alive, resolving 99% of layout logic bugs.
- **Panic Button (Hard Factory Reset):** Wipes everything completely. It deletes all custom workflows in the n8n backend, revokes all connected OAuth tokens, flushes the user profile database, and routes the user back to the initial onboarding screen.

## 8. Monetization & Subscription Strategy

A value-based pricing matrix aligned with user consumption to ensure high software profit margins.

| Subscription Tier | Pricing | Core Usage Limits | Key Features Included |
|---|---|---|---|
| **7-Day "Aha!" Trial** | $0 | Full Access for 7 Days | Guided Onboarding, App integrations, Live 24hr Mini-Digest testing. |
| **The Calm Tier** | $39 / mo | 1,000 processed items/mo; 500 library items saved; Max 10 smart feeds | Full Zen Dashboard, AI Guide, Routine Planner, Pre-verified n8n templates. High margin utilizing efficient LLM endpoints. |
| **The YOLO / Power Tier** | $99 / mo | 10,000 processed items/mo; 5,000 library items saved; Uncapped executions | Full Advanced Developer Sandbox access, Raw JSON editing, Custom LLM key injection, Priority execution queues. |
