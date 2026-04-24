# Integration Map

## Purpose

Define how the brain connects to each external service, what it can read and write, and which implementation approach is preferred.

## Integration Overview

| Service       | Direction          | Use Cases                                              | Approach                                           |
| ------------- | ------------------ | ------------------------------------------------------ | -------------------------------------------------- |
| Notion        | Read + Write       | Read pages and databases, create tasks, update entries | Notion API (official)                              |
| Google Drive  | Read + Write       | Read documents, create files, organize content         | Google Drive API via service account               |
| Gmail         | Read               | Read and summarize emails, flag important messages     | Gmail API via OAuth2                               |
| Gemini        | AI reasoning       | Task execution, analysis, drafting                      | Gemini API (primary AI employee provider)          |
| Notifications | Outbound           | Send alerts and updates to the user                    | Email and app-level channels                       |

---

## Optional Legacy Adapter: WhatsApp

### Purpose

- Legacy command adapter retained for compatibility if needed.
- Not a blocker for active roadmap execution.

### Implementation Options

| Option                               | Description                  | Trade-off                                          |
| ------------------------------------ | ---------------------------- | -------------------------------------------------- |
| Twilio WhatsApp API                  | Managed service, quick setup | Costs per message, Twilio dependency               |
| Meta WhatsApp Cloud API              | Official free tier, direct   | More setup, requires business verification         |
| WhatsApp Web automation (unofficial) | No business account needed   | Fragile, against Terms of Service, not recommended |

**Current position:** Optional only. Keep disabled unless explicitly required.

### Security Rule

If enabled, only messages from the owner's verified phone number are accepted as commands.

### Decision Required

Only required if WhatsApp is re-activated as an interface.

---

## Gemini (Primary AI Employee)

### Purpose

- Primary AI execution provider for analysis, planning, and drafting tasks.
- Default provider for AI employee workflows.

### Implementation Approach

- Gemini API as the default dispatcher provider.
- OpenAI/Anthropic may remain as optional fallback providers.

### Key Capabilities Needed

- Natural-language reasoning and drafting
- Structured prompt execution
- Stable model configuration via environment variables (`GEMINI_API_KEY`, `GEMINI_MODEL`)

---

## Notion

### Purpose

- Read strategy pages, task lists, and databases.
- Write AI-generated summaries, new entries, or updated task states.
- Mirror structured data from this repository into Notion for human review.

### Implementation Approach

- Official Notion API with an integration token.
- Scope: read content and create or update database rows.
- The brain never deletes Notion content without explicit user confirmation.

### Key Capabilities Needed

- Read database rows (tasks, goals, notes)
- Create new pages or rows
- Update page properties
- Search content by keyword

### Decision Required

Define which Notion databases or pages the brain should have access to.

---

## Google Drive

### Purpose

- Read documents for context (strategy docs, financial sheets, reference material).
- Create new documents with AI-generated content.
- Organize files into correct folders on command.

### Implementation Approach

- Google Drive API via a service account or OAuth2 user token.
- Scope: read files, create files, and move files within defined folders.
- The brain never deletes GDrive files without explicit user confirmation.

### Key Capabilities Needed

- Read file content (Docs, Sheets)
- Create new files
- Move or rename files
- List folder contents

### Decision Required

Define which Drive folders the brain has read and write access to.

---

## Gmail

### Purpose

- Read and triage the inbox.
- Summarize important emails on demand.
- Flag priority emails and notify through enabled notification channels.
- Draft reply templates on command (user approves before sending).

### Implementation Approach

- Gmail API via OAuth2.
- Scope: read-only access initially. Write access (drafts, sends) only added when explicitly needed.
- The brain never sends emails without explicit user confirmation.

### Key Capabilities Needed

- List and read messages
- Search by sender, subject, or label
- Create draft replies
- Mark emails as read or apply labels

### Security Rule

Email send permission requires an explicit user command with confirmation step.

---

## Notifications

### Purpose

- Push status updates, alerts, and reminders to the user proactively.
- Confirm that a command was received and executed.
- Alert on important events detected in connected services.

### Implementation Approach

- Primary channels: email and app-level interfaces.
- Optional channel: WhatsApp outbound adapter if explicitly enabled.
- Notification types: command confirmation, error alerts, scheduled digests, email summaries.
- Implemented scheduler: APScheduler background jobs inside the webhook process (`src/core/scheduler.py`).
- Reminder persistence: JSON store at `REMINDER_STORE_PATH` (default `data/reminders.json`).
- Implemented commands:
  - `remind me in <number> minutes|hours|days to <message>`
  - `remind me tomorrow at HH:MM to <message>`
  - `remind me at YYYY-MM-DD HH:MM to <message>`
  - `reminders`
- Optional daily Gmail digest is controlled by `DAILY_GMAIL_DIGEST_ENABLED`, `DAILY_GMAIL_DIGEST_HOUR`, and `DAILY_GMAIL_DIGEST_MINUTE`.

---

## Workflows (Stage 8)

### Purpose

- Combine multiple integrations into one compound user command.
- Reduce manual multi-step prompting by chaining operations in order.

### Current Implementation

- Workflow module: `src/core/workflows.py`
- Starter workflow command: `summarise my inbox and save to notion`
- Chain executed:
  1. Gmail inbox summary
  2. Notion page creation

### Required Setup

- `NOTION_API_TOKEN`
- `NOTION_WORKFLOW_PARENT_ID`
- Gmail OAuth2 credential flow (`GMAIL_CREDENTIALS_PATH`, token generation)

### Current Constraints

- Stage 8 is **in progress**: one chain is implemented; additional chains, confirmation steps, and richer error handling remain.

---

## Integration Development Rules

1. Document credentials and environment variables needed in `src/` before writing integration code.
2. Use environment variables for all secrets; never commit credentials.
3. Start every integration in read-only mode; add write permissions only when required.
4. Log integration decisions and scope changes in `docs/decisions/`.
5. Test each integration with a minimal script before wiring it into the brain's command router.
