# Personal Library System — Implementation Checklist

This is your step-by-step guide to building out the four personal knowledge libraries (Knowledge Base, Books, Articles, Thoughts). Use this to make choices and track progress.

> 2026-04-20 update: In this project, "library" now means local folder `library/` only. Stage 9 implementation should be filesystem-first. Notion-focused sections below are legacy references and should be translated to local markdown storage.

---

## Phase 0: Decision Point

### Choose Your Approach

**Quick-Start (1-2 hours)**

- Single local `library/` structure with 4 core content areas
- Minimal field schema
- Manual commands via WhatsApp (no automation yet)
- Best for: Testing, immediate use, learning your preferences

**Full (2-3 weeks)**

- Structured local folders for each library type with indexing/search
- Rich schema with relations and rollups
- Automated WhatsApp commands + intent detection
- AI-powered summaries and synthesis
- Best for: Long-term, scalable, integrated with command center

**Hybrid (1 week)**

- Quick-start local `library/` setup
- WhatsApp command handlers (Stage 9)
- Defer AI summaries and synthesis to later

### Recommendation

Start **Hybrid**: Quick Notion setup + command integration. This gives you immediate use while building infrastructure.

Updated recommendation: Start **Hybrid** with local `library/` setup + command integration.

---

## Phase 1: Notion Setup (2-3 hours)

### Step 1.0: Notion Integration Setup (latest flow)

Use this sequence before creating databases so API access works on first try.

1. Open Notion in browser.
2. Go to `Settings` -> `Connections` (or `My connections`) and create a new internal integration.
3. Name it `Solo Leveling Brain` (or your preferred name).
4. Copy the integration secret token immediately.
5. In your local repo `.env`, set:
   - `NOTION_API_TOKEN=<your integration token>`
   - `NOTION_WORKFLOW_PARENT_ID=<page id from target parent page URL>`
6. In Notion, create or open your parent page (recommended: `Personal Brain`).
7. Click `Share` on that page and invite your integration/connection.
8. Confirm the integration has access to the parent page and each library database you create.
9. Run verification command through your bot: `notion project`.
10. Run write test: `summarise my inbox and save to notion`.

If verification fails, check these in order:

- Token is present and correct in `.env`
- Parent page ID is correct
- Integration is invited to the specific page/database
- Server process was restarted after `.env` changes

### Step 1.1: Create the 4 Databases

In your Notion workspace, create 4 new databases:

**1. Knowledge Base Database**

Name: `Personal Knowledge Base`

Fields:

- [ ] **Term** (Text) — the word/acronym/concept
- [ ] **Definition** (Rich Text) — 2-3 sentence explanation
- [ ] **Category** (Select) — Technology | Finance | Philosophy | Health | Psychology | Business | Other
- [ ] **Tags** (Multi-select) — core-concept, reference, acronym, frequently-used, fuzzy, important
- [ ] **Examples** (Rich Text) — how you use this in practice
- [ ] **Source** (Text) — where you learned it (book, article, person, experience)
- [ ] **Related Terms** (Relation) — link to other Terms (backlinks)
- [ ] **Date Added** (Date)
- [ ] **Last Reviewed** (Date)
- [ ] **Review Count** (Number) — for spaced repetition tracking

Template Button: "New Term" (pre-fill today's date)

---

**2. Books Database**

Name: `My Book Library`

Fields:

- [ ] **Title** (Title) — book title
- [ ] **Author** (Text)
- [ ] **Status** (Select) — Wishlist | Reading | Read | Abandoned | Re-reading
- [ ] **Started** (Date)
- [ ] **Completed** (Date)
- [ ] **Rating** (Number, 1-5)
- [ ] **Key Insights** (Rich Text) — 3-5 bullet points
- [ ] **Summary** (Rich Text) — 1-2 paragraph personal summary
- [ ] **Topics** (Multi-select) — finance, psychology, business, health, technology, narrative, biography, etc.
- [ ] **Quotes** (Relation) — to Quotes database (optional, for later)
- [ ] **Transcript Link** (URL) — if audiobook/video version
- [ ] **Drive Folder** (Text) — path to book materials on Drive
- [ ] **Video Resume** (URL) — if you create video summary
- [ ] **Next Action** (Text) — what to do with this knowledge
- [ ] **Date Added** (Date)

Views:

- [ ] "Currently Reading" (filter: Status = Reading)
- [ ] "Finished" (filter: Status = Read)
- [ ] "By Topic" (group by Topics)
- [ ] "High Rated" (filter: Rating >= 4, sort by Completed date)

Template Button: "Add New Book" (pre-fill Date Added)

---

**3. Articles Database**

Name: `Article Library`

Fields:

- [ ] **Title** (Title)
- [ ] **URL** (URL)
- [ ] **Author/Source** (Text)
- [ ] **Published Date** (Date)
- [ ] **Date Saved** (Date)
- [ ] **Topics** (Multi-select) — engineering, finance, health, philosophy, psychology, business, etc.
- [ ] **Relevance** (Select) — Bookmark | Reference | Deep Dive | To Read
- [ ] **Summary** (Rich Text) — 1-3 sentences
- [ ] **Key Points** (Rich Text) — bullet list
- [ ] **Personal Insight** (Rich Text) — what this means to you
- [ ] **Status** (Select) — To Read | Reading | Read | Synthesized
- [ ] **Drive Backup** (URL) — link to Drive copy if archived
- [ ] **Date Last Reviewed** (Date)

Views:

- [ ] "To Read" (filter: Status = To Read)
- [ ] "By Topic" (group by Topics)
- [ ] "Recent Saves" (sort by Date Saved desc)
- [ ] "Deep Dives" (filter: Relevance = Deep Dive)

Template Button: "Save New Article" (auto-fetch URL)

---

**4. Personal Thoughts Database**

Name: `Thought Drafts`

Fields:

- [ ] **Title** (Title) — framework/insight name
- [ ] **Type** (Select) — Framework | Insight | Decision | Question | Essay | Work in Progress
- [ ] **Status** (Select) — Draft | Exploring | Published | Archived
- [ ] **Created** (Date)
- [ ] **Last Updated** (Date)
- [ ] **Topics** (Multi-select) — personal-philosophy, business-model, financial-freedom, learning, etc.
- [ ] **Related Books** (Relation) — link to Books DB
- [ ] **Related Articles** (Relation) — link to Articles DB
- [ ] **Word Count** (Number)
- [ ] **Confidence** (Select) — High | Medium | Low | Exploring
- [ ] **Next Steps** (Text) — what's needed to complete
- [ ] **Drive Doc Link** (URL) — link to full document on Drive
- [ ] **Summary** (Rich Text) — 1-sentence pitch

Views:

- [ ] "Drafts" (filter: Status = Draft or Exploring)
- [ ] "Published" (filter: Status = Published)
- [ ] "By Type" (group by Type)
- [ ] "In Progress" (filter: Status = Exploring)

Template Button: "New Thought" (pre-fill dates and status=Draft)

---

### Step 1.2: Create Google Drive Folders

```
/Google Drive/

Personal Library/
  ├── Books/
  │   ├── [Author Name] - [Title]/
  │   │   ├── Summary.md
  │   │   ├── Key Quotes.txt
  │   │   ├── Video Transcript.md (if exists)
  │   │   ├── Personal Notes.md
  │   │   └── Action Items.txt
  │
  ├── Articles/
  │   ├── By Topic/
  │   │   ├── Engineering/
  │   │   ├── Finance/
  │   │   └── Health/
  │   └── Archive/ (old articles)
  │
  └── Personal Drafts/
      ├── Frameworks/
      │   ├── [Framework Name].md
      ├── Essays/
      │   ├── [Topic] - [Date].md
      ├── Questions/
      │   ├── [Question].md
      └── Work in Progress/
          └── [Project Name]/
```

---

## Phase 2: Manual Testing (1 hour)

Before automation, test manually:

### Test 1.1: Add a Term

1. Open "Personal Knowledge Base" database
2. Click "Add New Term"
3. Fill:
   - Term: "PKM"
   - Definition: "Personal Knowledge Management — the practice of capturing, organizing, and retrieving personal learning and insights."
   - Category: Technology
   - Tags: [acronym, core-concept]
   - Source: "My research today"
4. Save

### Test 1.2: Add a Book

1. Open "My Book Library" database
2. Click "Add New Book"
3. Fill:
   - Title: "Atomic Habits"
   - Author: "James Clear"
   - Status: Read
   - Completed: [today's date]
   - Rating: 5
   - Summary: "Framework for habit change using small, consistent actions..."
   - Topics: [psychology, business]
4. Create Drive folder: `/Personal Library/Books/James Clear - Atomic Habits/`
5. Save

### Test 1.3: Add an Article

1. Open "Article Library" database
2. Click "Save New Article"
3. Paste URL and fill fields
4. Save

### Test 1.4: Capture a Thought

1. Open "Thought Drafts" database
2. Click "New Thought"
3. Title: "Personal Operating System Design"
4. Type: Framework
5. Status: Exploring
6. Summary: "Multi-layered system combining habit loops, goal tracking, knowledge capture, and AI-assisted review"
7. Save

---

## Phase 3: WhatsApp Command Integration (1-2 weeks)

### 3.0: Add Knowledge Profile Commands (skills, interests, domains)

Use profile commands to capture your personal learning identity without storing sensitive data.

Command templates:

- `profile skill: <name> | confidence: <high|medium|low|exploring> | priority: <now|next|later>`
- `profile interest: <topic> | priority: <now|next|later>`
- `profile domain: <domain> | focus: <short note>`
- `profile update: <item> | <new value>`
- `profile summary`

Validation rules:

- Reject unknown enum values with a clear correction hint.
- Require `profile type` and `profile item` on create.
- Never accept credentials, legal IDs, private contact records, or sensitive financial values through profile commands.

### 3.1: Extend Router (src/core/router.py)

Add new intents:

```python
INTENT_MAP: dict[str, list[str]] = {
    # ... existing intents ...
    "library_profile": ["profile skill", "profile interest", "profile domain", "profile update", "profile summary"],
    "library_term": ["term", "definition", "acronym", "add term", "define"],
    "library_book": ["book:", "add book", "reading", "finished", "book insights"],
    "library_article": ["article:", "save article", "articles on"],
    "library_thought": ["thought:", "draft:", "my thoughts"],
    "library_review": ["review terms", "review books", "my library", "library status"],
}
```

---

### 3.2: Create Handler (src/core/libraries.py)

```python
"""
Stage 9: Personal knowledge library handlers.

Manages capture, organization, and retrieval of:
  - Knowledge Base (terms, definitions, acronyms)
  - Books Library (with summaries, transcripts, notes)
  - Articles Library (with summaries, links, topics)
  - Thought Drafts (frameworks, insights, essays)
"""

from src.integrations.notion import client as notion

def handle_library_command(text: str, intent: str) -> str:
    """Route library command to the right handler."""

    if intent == "library_profile":
        return _handle_profile(text)
    if intent == "library_term":
        return _handle_term(text)
    elif intent == "library_book":
        return _handle_book(text)
    elif intent == "library_article":
        return _handle_article(text)
    elif intent == "library_thought":
        return _handle_thought(text)
    elif intent == "library_review":
        return _handle_review(text)

    return "Library command not recognized."

def _handle_profile(text: str) -> str:
    """Capture or retrieve knowledge profile data (skills, interests, domains)."""
    # Parse profile create/update/summary commands
    # Validate allowed profile types and enum values
    # Reject sensitive categories outside profile scope
    pass

def _handle_term(text: str) -> str:
    """Capture or retrieve a term."""
    # Parse: "term: <word>" or "define <word>"
    # If starts with "term:" or "add term:" → create
    # If starts with "term " → search
    pass

def _handle_book(text: str) -> str:
    """Capture or retrieve book info."""
    # Parse: "book: <title> by <author>" → create
    # "reading <title>" → update status
    # "finished <title>" → mark complete
    # "book insights: <title>" → retrieve
    pass

def _handle_article(text: str) -> str:
    """Capture or retrieve article."""
    # Parse: "article: <url>" → fetch + create
    # "articles on <topic>" → search
    pass

def _handle_thought(text: str) -> str:
    """Capture or refine a personal thought."""
    # Parse: "thought: <idea>" → create
    # "draft: <title>" → retrieve/list
    # "publish: <title>" → mark as published
    pass

def _handle_review(text: str) -> str:
    """Retrieve library stats and review items."""
    # "my library" → summary stats
    # "review terms" → pick 5 random terms for spaced repetition
    # "review books" → list unfinished books
    pass
```

---

### 3.3: Wire Into Router

In `src/core/router.py`, update `_dispatch()`:

```python
def _dispatch(intent: str, original_text: str) -> str:
    handlers = {
        # ... existing handlers ...
        "library_profile": _handle_library,
        "library_term": _handle_library,
        "library_book": _handle_library,
        "library_article": _handle_library,
        "library_thought": _handle_library,
        "library_review": _handle_library,
    }
    handler = handlers.get(intent, _handle_unknown)
    # ... existing error handling ...
```

---

## Phase 4: AI Enhancement (Optional, weeks 2-3)

### 4.1: Auto-Summarize Books/Articles

When user saves a book or article with a URL, use AI agent to:

- Fetch page content (articles)
- Generate summary
- Extract key points
- Suggest topics

### 4.4: MCP Profile Contracts

- [ ] Define MCP tools: `create_profile_item`, `update_profile_item`, `search_profile_items`, `summarize_profile`
- [ ] Define MCP resources: `/profile/recent-updates`, `/profile/domain-map`, `/profile/learning-priorities`
- [ ] Add profile-aware prompt templates for planning and weekly review
- [ ] Ensure every tool input/output is schema-validated

### 4.2: Monthly Synthesis

Create Stage 9 workflow: "synthesize my library"

- Fetch all items added/updated this month
- Use AI to identify patterns, themes, connections
- Generate monthly insight report
- Add related items to Thought Drafts

### 4.3: Spaced Repetition

On "review terms":

- Pick terms least recently reviewed
- Display 5 random terms
- Ask user to recall definition
- Log review date and count

---

## Success Checklist

**By End of Phase 1:**

- [ ] 4 Notion databases created and accessible
- [ ] Google Drive folder structure ready
- [ ] You've manually added 3-5 items to each library
- [ ] Templates/buttons working

**By End of Phase 2:**

- [ ] WhatsApp commands working for each library type
- [ ] New items auto-created in Notion from WhatsApp
- [ ] Can retrieve items via WhatsApp

**By End of Phase 3:**

- [ ] Book/article summaries auto-generated
- [ ] Monthly synthesis running
- [ ] Spaced repetition review working

**Long-term Success:**

- [ ] 50+ items per month added across all libraries
- [ ] 80%+ review adherence (monthly review habit)
- [ ] 3+ thoughts synthesized into action or shared work
- [ ] Library frequently consulted for decisions/reference

---

## What Happens Next

Once libraries are live:

1. **Notion Dashboard**: Create summary page showing library stats, recent additions, pending reviews
2. **Integration**: Link findings to financial planning and self-development goals
3. **Automation**: Set up monthly reminders to review and synthesize
4. **Evolution**: Add personal projects library, decision log integration, learning roadmap

---

## Questions to Refine Your Structure

Before you start, answer these to tailor the schema:

1. **Books**: Do you want to track individual quotes separately? (requires a Quotes database)
2. **Articles**: How many articles per month do you typically save? (affects review frequency)
3. **Thoughts**: Do you want to publish thoughts as blog posts? (affects workflow and Drive sync)
4. **Knowledge Base**: How do you prefer to learn? (Spaced repetition vs. manual review)
5. **Priority**: Which library should be built first? (Start with highest-value to you)
