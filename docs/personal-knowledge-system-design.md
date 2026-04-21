# Personal Knowledge System Design

> 2026-04-20 update: In this repo, **library** now means the local `library/` folder only. Any historical Notion-library wording below is legacy context and should be implemented as local file storage going forward.

## Research: Self-Development Strategies & Knowledge Management

### MCP Knowledge Pack (for your library)

Use this as a ready-to-store knowledge bundle in your `Personal Knowledge Base`.

**Term: MCP**

- **Full form:** Model Context Protocol
- **Definition:** An open protocol that standardizes how AI models connect to external tools, data sources, and actions using a consistent interface.
- **Why it matters for your repo:** Your command-center design already routes AI tasks across services (Notion, Gmail, Drive, WhatsApp). MCP gives a cleaner, reusable pattern for tool discovery, context exchange, and execution.

**Core MCP concepts to store as terms**

1. **Host**

- The AI application runtime that orchestrates model calls and tool usage.
- In your case, the command center is a host-like layer.

2. **Client**

- The component that connects from the host to an MCP server.
- Responsible for capability negotiation and calling tools.

3. **Server**

- A process exposing tools/resources/prompts through MCP.
- Can wrap services like Notion, Drive, filesystem, or internal business logic.

4. **Tool**

- Callable function exposed by an MCP server (input schema + output schema).
- Example: `create_notion_page`, `query_books_library`, `summarise_articles`.

5. **Resource**

- Read-focused data endpoint exposed through MCP.
- Example: latest notes, database views, saved article summaries.

6. **Prompt**

- Reusable prompt template exposed by the server.
- Useful for standardized outputs (weekly review, synthesis report, decision memo).

7. **Schema-first contracts**

- MCP tools/resources are strongly structured (JSON schema-like contracts).
- Reduces ambiguity and improves reliability across agents.

8. **Capability negotiation**

- Host/client can discover what a server supports before calling it.
- Avoids hardcoded assumptions and helps multi-agent portability.

**Practical MCP adoption path for this repo**

1. Start with a local `library` MCP server that exposes your 4 personal libraries as tools/resources.
2. Keep existing router behavior; introduce MCP as an abstraction layer behind handlers.
3. Move repeated integration actions (Notion create/search, Drive write/read) into MCP tools.
4. Add prompts for recurring outputs: weekly self-review, monthly knowledge synthesis.
5. Use schema-validated inputs to make WhatsApp commands safer and less error-prone.

### Knowledge Profile (Phase 1 personal information scope)

For the first rollout, personal information capture should stay focused on knowledge profile data only:

- Skills and capability areas
- Interests and curiosity areas
- Domains of focus (for example: business, psychology, engineering)
- Learning priorities and current focus themes

Do not store sensitive personal data in this phase (credentials, legal IDs, private contact data, or sensitive financial values).

**Profile schema extension (MCP-ready):**

```
{
  Profile Item: text
  Profile Type: select (Skill, Interest, Domain, Learning Priority, Focus Theme)
  Description: rich_text
  Confidence: select (High, Medium, Low, Exploring)
  Priority: select (Now, Next, Later)
  Related Terms: relation
  Related Books: relation
  Related Articles: relation
  Related Thoughts: relation
  Last Updated: date
  Source: text
}
```

**MCP tool contracts for profile lifecycle:**

- `create_profile_item` (validated create)
- `update_profile_item` (validated patch)
- `search_profile_items` (filter by type/topic/priority)
- `summarize_profile` (state snapshot for planning)

**MCP resources for agent grounding:**

- `/profile/recent-updates`
- `/profile/domain-map`
- `/profile/learning-priorities`

**MCP prompt templates for agents:**

- `profile_aware_planning`
- `profile_aware_retrieval`
- `weekly_profile_review`

### Implementation trends to adopt

- Schema-first contracts for all tool inputs/outputs to reduce command ambiguity.
- Provenance-first captures (include `Source` and `Last Updated`) for traceable memory.
- Small, composable tools over large monolithic commands to improve multi-agent reuse.
- Git-tracked synthesis outputs (weekly or monthly) so learning evolution is reviewable.

### Self-Development Frameworks

**1. Deliberate Practice Model (Ericsson)**

- Focus: Structured, targeted skill building
- Core: Regular feedback loops, progressive complexity, focused effort
- Best for: Technical skills, language learning, specialized domains

**2. Atomic Habits Framework (Clear)**

- Focus: Systems over goals, identity-based habits, environmental design
- Core: Habit stacking, trigger → routine → reward, measurement
- Best for: Behavioral change, consistency, compound effects over time

**3. 70-20-10 Learning Model**

- 70% learning from work/real challenges
- 20% learning from relationships, mentoring, feedback
- 10% learning from formal education
- Application: Balance practical experience with knowledge capture

**4. Spaced Repetition & Active Recall (Ebbinghaus)**

- Core: Revisit knowledge at optimal intervals before forgetting
- Best for: Retention, long-term memory, language/terminology
- Tools: Flashcard systems, periodic reviews, deliberate re-engagement

**5. Zettelkasten Method (Luhmann)**

- Core: Atomic notes, bidirectional linking, knowledge graph emergence
- Process: Capture → Process → Link → Review → Create
- Best for: Deep thinking, synthesis, avoiding knowledge debt

---

## Personal Knowledge System Analysis

Your needs map to **4 distinct library types**, each with different capture, storage, and usage patterns:

| Library Type         | Core Content                         | Access Pattern            | Update Frequency | Best Storage                     |
| -------------------- | ------------------------------------ | ------------------------- | ---------------- | -------------------------------- |
| **Knowledge Base**   | Definitions, acronyms, reference     | Lookup, search            | On-demand        | `library/terms/` + tags          |
| **Books Library**    | Collections, transcripts, summaries  | Browse, search, reference | Monthly          | `library/books/` + Drive         |
| **Articles Library** | Links, summaries, insights           | Skim, search, recommend   | Weekly           | `library/articles/` + Drive      |
| **Thought Drafts**   | Personal reasoning, work-in-progress | Capture, refine, publish  | Frequent         | `library/thoughts/` + Drive docs |

---

## Recommended Architecture

### Core Principle: Capture → Process → Link → Retrieve

```
WhatsApp Command
    ↓
"save book: <title> by <author>" / "new thought: <idea>" / "article: <url>"
    ↓
Router detects intent (book, article, thought, term)
    ↓
Handler creates record in local `library/` markdown (title, date, content, tags, status)
    ↓
Optional: Generate summary via AI agent
    ↓
Link to related records (backlinks, topic tags)
    ↓
Drive backup for long-form content
    ↓
Monthly review workflow (AI-assisted synthesis)
```

### Library Structure

#### 1. **Knowledge Base Library** (`library/terms/`)

Purpose: Searchable dictionary of personal reference knowledge

**Schema:**

```
{
  Term: text
  Definition: rich_text (2-3 sentences)
  Category: select (Technology, Finance, Philosophy, Health, ...)
  Tags: multi_select (e.g., #core-concept, #reference, #acronym)
  Related Terms: relation (backlinks)
  Examples: rich_text (how/where you use this)
  Source: text (where you learned it)
  Date Added: date
  Last Reviewed: date
  Review Count: number (for spaced repetition tracking)
}
```

**WhatsApp Commands:**

- `term <word>` — lookup definition
- `add term: <word> = <definition>` — capture new term
- `review terms` — get 5 random terms for review

---

#### 2. **Books Library** (`library/books/` + Drive)

Purpose: Personal book collection with notes, summaries, and transcripts

**Schema:**

```
{
  Title: text
  Author: text
  Status: select (Reading, Read, Abandoned, Wishlist, Re-reading)
  Started: date
  Completed: date
  Rating: number (1-5)
  Key Insights: rich_text (3-5 bullet points)
  Personal Summary: rich_text (1-2 paragraphs)
  Topics: multi_select (e.g., #finance, #psychology, #business)
  Quotes: relation (to Quotes database)
  Transcript Link: url (if audiobook/video)
  Drive Folder: text (path to book materials)
  Video Resume: url (if you create video summary)
  Next Action: text (what to do with this knowledge)
  Date Added: date
}
```

**Drive Structure:**

```
/Google Drive/Books/
  ├── [Author Name] - [Book Title]/
  │   ├── Summary.md
  │   ├── Key Quotes.txt
  │   ├── Video Transcript.md
  │   ├── Personal Notes.md
  │   └── Action Items.txt
```

**WhatsApp Commands:**

- `book: <title> by <author>` — add new book (stub)
- `reading <title>` — mark as currently reading
- `finished <title>` — mark as complete with optional rating
- `book insights: <title>` — get key insights for a book
- `books on <topic>` — list books in a category

---

#### 3. **Articles Library** (`library/articles/` + Drive)

Purpose: Curated collection of articles with summaries and linkback to original

**Schema:**

```
{
  Title: text
  URL: url
  Author/Source: text
  Published Date: date
  Date Saved: date
  Topic: multi_select (e.g., #engineering, #finance, #health)
  Relevance: select (Bookmark, Reference, Deep Dive, To Read)
  Summary: rich_text (1-3 sentences)
  Key Points: rich_text (bullet list)
  Personal Insight: rich_text (what this means to me)
  Related Articles: relation (cross-references)
  Related Books: relation (if book exists)
  Status: select (To Read, Read, Synthesized)
  Drive Backup: url (link to Drive copy if needed)
  Date Last Reviewed: date
}
```

**Drive Structure:**

```
/Google Drive/Articles/
  ├── By Topic/
  │   ├── Engineering/
  │   ├── Finance/
  │   └── Health/
  └── By Year/
      ├── 2026/
      └── 2025/
```

**WhatsApp Commands:**

- `article: <url>` — save new article (auto-fetch title)
- `article: <topic>` — list articles in topic
- `articles to read` — list unread articles
- `article summary: <title>` — get summary

---

#### 4. **Thought Drafts Library** (`library/thoughts/` + Drive Docs)

Purpose: Capture evolving personal reasoning, frameworks, and insights

**Schema:**

```
{
  Title: text
  Type: select (Framework, Insight, Decision, Question, Essay, Work in Progress)
  Status: select (Draft, Exploring, Published, Archived)
  Created: date
  Last Updated: date
  Related Topics: multi_select
  Related Books: relation
  Related Articles: relation
  Word Count: number
  Confidence: select (High, Medium, Low, Exploring)
  Next Steps: text (what's needed to complete)
  Drive Doc Link: url
  Tags: multi_select (e.g., #personal-philosophy, #business-model, #financial-freedom)
  Summary: rich_text (1-sentence pitch)
}
```

**Drive Structure:**

```
/Google Drive/Personal Drafts/
  ├── Frameworks/
  │   ├── [Framework Name].md
  ├── Essays/
  │   ├── [Topic] - [Date].md
  ├── Questions/
  │   ├── [Question].md
  └── Work in Progress/
      ├── [Project Name]/
```

**WhatsApp Commands:**

- `thought: <idea>` — start new thought capture
- `draft: <title>` — list all drafts matching title
- `publish thought: <title>` — mark as complete
- `thoughts on <topic>` — list thoughts in topic

---

## Integration with Command Center

### New Stage 9: Personal Knowledge Management

Extend router and workflows to handle library commands

**New intents in router:**

```python
"knowledge_term": ["term", "definition", "acronym", "add term"],
"book_save": ["book:", "add book", "reading", "finished"],
"article_save": ["article:", "save article"],
"thought_capture": ["thought:", "draft:"],
"library_review": ["review terms", "review books", "my library"],
```

**New workflow chains:**

1. "save book X and create summary" → `library/books/` + Drive folder + AI summary
2. "save article and add to <topic>" → `library/articles/` + topic tag
3. "capture thought and link to <topic>" → `library/thoughts/` + Drive doc
4. "what's my library status" → count/summary of all libraries

### Local Library Hierarchy

```
library/
  ├── profile/
  ├── terms/
  ├── books/
  ├── articles/
  ├── thoughts/
  └── references/
```

---

## Implementation Plan

### Phase 1: Structure & Setup (Week 1)

- [ ] Create and validate `library/` subfolders (profile, terms, books, articles, thoughts, references)
- [ ] Set up Google Drive folder structure
- [ ] Create database templates (summary templates for each type)
- [ ] Document access patterns (how to retrieve, search, link)

### Phase 2: Command Integration (Week 2)

- [ ] Implement WhatsApp → local library handlers for each library type
- [ ] Add intent detection to router
- [ ] Create workflow handlers for multi-step captures
- [ ] Test basic: save book, save article, capture thought

### Phase 3: AI Enhancement (Week 3)

- [ ] Auto-generate book/article summaries via AI agent
- [ ] Monthly synthesis: AI-powered insight generation across all libraries
- [ ] Auto-tagging and topic suggestion via embeddings
- [ ] Create review prompts for spaced repetition

### Phase 4: Advanced Features (Week 4+)

- [ ] Dashboard showing library stats and activity
- [ ] Related item suggestions (article → similar books)
- [ ] Thought-to-article workflow (refine draft → publish)
- [ ] Export/archive strategies

---

## Quick-Start Schema (Minimal Viable)

If you want to start immediately without full infrastructure:

**Single Local Folder with 4 Core Views:**

- View 1: Terms (Type = Term, Status = Active)
- View 2: Books (Type = Book, filters by Status)
- View 3: Articles (Type = Article, filters by Status)
- View 4: Thoughts (Type = Thought, filters by Status)

**Unified schema:**

```
{
  Type: select (Term, Book, Article, Thought)
  Title: text
  Content/Summary: rich_text
  URL: url (for articles)
  Author: text (for books/articles)
  Status: select
  Topics: multi_select
  Date Added: date
  Drive Link: url
}
```

---

## Success Metrics

**Knowledge Capture:**

- Items added per week (target: 5-10)
- Library growth rate (target: 50 items/month)

**Knowledge Retention (Spaced Repetition):**

- Terms reviewed per month
- Review consistency (target: 80% adherence)

**Knowledge Synthesis:**

- Connections made between items (via backlinks)
- Monthly insights generated
- Thought-to-action conversions (drafts → shared/acted on)

**Quality:**

- Re-engagement rate (what % revisited?)
- Value delivery (did this library actually help a decision?)

---

## Next Steps

1. **Decide: Quick-start or Full?**
   - Quick-start: Master DB with 4 views (ready in hours)
   - Full: Separate DBs, Drive folders, AI integration (weeks)

2. **Setup:**

- Create local `library/` folder structure
- Set up Google Drive structure
- Document template examples

3. **Integrate:**
   - Add WhatsApp commands to router
   - Create handlers in `src/core/libraries.py`
   - Test end-to-end flow

4. **Enhance:**
   - Implement AI summaries
   - Add monthly synthesis
   - Build dashboard/stats views
