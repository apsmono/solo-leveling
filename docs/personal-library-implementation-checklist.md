# Personal Library System — Implementation Checklist

This is the step-by-step guide for the Stage 9 personal knowledge library stored in the local `library/` folder. The core content areas are terms, books, articles, thoughts, profile items, references, and research bundles.

> 2026-04-20 update: In this project, "library" now means local folder `library/` only. Stage 9 storage, retrieval, search, summaries, and formatting all run against the filesystem. Older Notion database sections in this file are historical schema references only.

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

Start **Hybrid**: local `library/` setup + command integration + indexed retrieval. This gives you immediate use while keeping the storage model aligned with the live code.

---

## Phase 1: Local Library Bootstrap (current path)

### Step 1.0: Bootstrap Local Library

Use this sequence before adding Stage 9 knowledge so the local structure, formatting guide, and retrieval index are ready.

1. Confirm the repository contains the canonical Stage 9 folders under `library/`.
2. Run the `library guide` command once so the formatting standard is saved into `library/references/`.
3. Test one direct write for each core type:
    - `add term: <term> = <definition>`
    - `book: <title> by <author>`
    - `article: <url or title>`
    - `thought: <idea with enough detail>`
4. Test one deep capture command:
    - `add to library: <topic>`
5. Test retrieval commands:
    - `search library: <query>`
    - `library bundle: <topic>`
    - `summarize library: <topic>`
6. Confirm `library/index.json` refreshes after each new write.
7. Keep Notion credentials only for the existing Notion integration features outside Stage 9 storage.

If verification fails, check these in order:

- The command matches the expected Stage 9 format
- The write was not blocked by sensitive-content detection
- The target file or bundle was created under the expected `library/` subfolder
- `library/index.json` exists and was refreshed after the write

### Step 1.1: Historical Schema Reference (legacy only)

The sections below preserve the original four-library schema research. They are no longer the implementation instructions for Stage 9 storage. Use them only as naming, metadata, or taxonomy reference when refining local markdown formats.

### Step 1.2: Legacy Four-Library Model

Historical reference: the four primary areas still map conceptually to local storage like this:

- Knowledge Base -> `library/terms/`
- Books -> `library/books/`
- Articles -> `library/articles/`
- Thoughts -> `library/thoughts/`

Original database notes retained below:

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
Stage 9: Personal knowledge library handlers backed by the local `library/` folder.

Manages capture, organization, and retrieval of:
    - Terms and definitions
    - Books with summaries and notes
    - Articles with links and topics
    - Thought drafts and updates
    - Research bundles for deep captures
"""

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

- [ ] `library/` folders exist and match the Stage 9 structure
- [ ] `library guide` has been saved into `library/references/`
- [ ] You've manually added 3-5 items across the local library
- [ ] `library/index.json` refreshes after new writes

**By End of Phase 2:**

- [ ] WhatsApp commands working for each library type
- [ ] New items auto-created in local `library/` storage from WhatsApp
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

1. **Library Dashboard**: create a local or generated summary view showing library stats, recent additions, pending reviews, and bundle activity
2. **Integration**: Link findings to financial planning and self-development goals
3. **Automation**: Set up monthly reminders to review and synthesize
4. **Evolution**: Add personal projects library, decision log integration, learning roadmap

---

## Questions to Refine Your Structure

Before you start, answer these to tailor the schema:

1. **Books**: Do you want to track individual quotes separately? (could become a dedicated local section or linked note pattern)
2. **Articles**: How many articles per month do you typically save? (affects review frequency)
3. **Thoughts**: Do you want to publish thoughts as blog posts? (affects workflow and Drive sync)
4. **Knowledge Base**: How do you prefer to learn? (Spaced repetition vs. manual review)
5. **Priority**: Which library should be built first? (Start with highest-value to you)
