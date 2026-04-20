# Personal Library Formatting Guide

Last updated: 2026-04-18

This guide establishes human-readable, scannable standards for all Stage 9 Personal Knowledge Libraries in the local `library/` folder. Every new entry follows this format to keep your library organized, maintainable, and useful.

## Universal Style Rules

1. **One-screen readability**: First screen should immediately show what it is, why it matters, and current status.
2. **Keep writing short**: Summaries use 2-4 bullets; paragraphs max 3 lines; no single paragraph over 5 sentences.
3. **Consistent field order everywhere**: Use the 9-field standard across all database types.
4. **Prefer relations over copy-paste**: Link to existing entries instead of duplicating notes.
5. **Use fixed status vocabulary only**: No ad-hoc status words; stick to predefined lists per type.
6. **Every entry must have both date and tag**: Minimum requirements for any capture.
7. **Archive instead of delete**: Deprecated entries go to Archive view, not the trash.

## 9-Field Order (All Types)

Apply this order to **ALL** library entries for consistent markdown structure and retrieval readability:

1. **Title** — page name
2. **Type or Category** — what kind of item
3. **Status** — current state
4. **Priority or Confidence** — urgency or certainty level
5. **Summary or Definition** — 1-2 sentence core idea
6. **Key Points** — 3-5 bullet points
7. **Relations** — links to related entries
8. **Source** — where this came from
9. **Date Added / Updated / Reviewed** — timestamp

---

## Format Per Information Type

### Research Bundles / Deep Knowledge Intake

Use this format when the request is broad, strategic, ambiguous, or explicitly asks to "add to library" / "add to my personal knowledge".

**Storage rule**:

- Save as a folder bundle under the best-fit library section or `library/research/`
- Always preserve raw input, processing trail, and conclusion

**Must-have files**:

- `index.md` — categorized summary and why it matters
- `01-raw-input.md` — exact original material
- `02-search-history.md` — what was searched, matched, or inferred
- `03-research-notes.md` — relevant findings
- `04-information-to-track.md` — valuable facts, metrics, entities, or questions to monitor
- `05-qa-log.md` — internal Q/A used to clarify the topic
- `06-logic-trail.md` — reasoning and categorization logic
- `07-conclusion.md` — final conclusion, open questions, and next action

**What counts as valuable information to track**:

- Definitions and core claims
- Decision relevance and practical use
- Key entities, people, tools, frameworks, or metrics
- Open questions and uncertainty points
- Follow-up actions, experiments, or review dates

---

### Knowledge Profile (Skills, Interests, Domains)

**Best title style**: `Skill — Python Automation` or `Domain — Financial Systems`

**Must-have fields**:

- Profile Type (Skill / Interest / Domain / Learning Priority / Focus Theme)
- Confidence (High / Medium / Low / Exploring)
- Priority (Now / Next / Later)
- Description (1-2 sentences)
- Related Items (relations to other profile entries)
- Last Updated (date)

**Page sections (in order)**:

1. **Snapshot** — 1-sentence summary
2. **Current Level / Confidence** — where you stand right now
3. **Evidence** — projects, books, articles supporting this claim
4. **Next Step** — what you'll do next to advance this

**Recommended views**:

- By Type
- Priority Now
- Confidence Low (learning focus)
- Recently Updated

---

### Terms / Concepts

**Best title style**: `MCP`, `Spaced Repetition`, `Cashflow Forecast`

**Must-have fields**:

- Definition (2-3 sentences)
- Category (Framework / Principle / Tool / Pattern)
- Example (how you've used it)
- Related Terms (relations)
- Last Reviewed (date)

**Page sections (in order)**:

1. **Plain Definition** — 2 sentences, no jargon
2. **Why It Matters** — context for why you care
3. **Example in Your System** — real case from your work
4. **Related Terms** — links to connected concepts

**Recommended views**:

- Core Concepts
- Needs Review (not reviewed in 60+ days)
- By Category
- Alphabetical

---

### Books

**Best title style**: `Author — Title` (e.g., `Feynman — Surely You're Joking, Mr. Feynman`)

**Must-have fields**:

- Author
- Status (Wishlist / Reading / Finished)
- Rating (1-5 scale, or blank if not finished)
- Key Insights (top 3 learning points)
- Summary (1-paragraph takeaway)
- Topics (tags like #learning, #finance, #psychology)
- Next Action (what to do with this learning)

**Page sections (in order)**:

1. **Quick Verdict** — 1-2 lines on whether it's worth reading
2. **Top 3 Insights** — most actionable ideas
3. **Supporting Notes** — key passages, quotes, deeper thoughts
4. **Related Thoughts** — links to other entries this connects to

**Recommended views**:

- Reading Now
- Finished (sorted by Rating descending)
- High Value (Rating >= 4)
- By Topic
- Recently Added

---

### Articles

**Best title style**: `Source — Headline`

**Must-have fields**:

- URL (with full link to source)
- Status (To Read / Deep Dive / Synthesized)
- Relevance (High / Medium / Low)
- Summary (1-3 sentence takeaway)
- Key Points (3-5 bullets)
- Personal Insight (what changes for you)
- Tags (lowercase-hyphen, max 5)

**Page sections (in order)**:

1. **One-line Thesis** — core claim
2. **Key Points** — 3 bullets from article
3. **Personal Insight** — how applies to your situation
4. **Related Links / Entries** — connections

**Recommended views**:

- To Read
- Deep Dive
- Synthesized
- By Relevance
- Recent Saves

---

### Thoughts / Drafts

**Best title style**: `Type — Topic` (e.g., `Framework — Learning Loop`)

**Must-have fields**:

- Type (Framework / Decision / Experiment / Observation / Question)
- Status (Draft / Exploring / Ready to Publish / Published)
- Confidence (High / Medium / Low)
- Core Idea (1-2 sentences)
- Supporting Arguments (key reasoning)
- Open Questions (uncertainties)
- Next Step (what happens next)

**Page sections (in order)**:

1. **Core Idea** — main point in 2-3 sentences
2. **Supporting Arguments** — 3-5 reasons or examples
3. **Open Questions** — gaps to resolve
4. **Next Step** — what you'll do to advance

**Recommended views**:

- Drafts
- Exploring
- Ready to Publish
- Low Confidence (for focused editing)
- Archived

---

## Naming and Tagging Standard

### Titles

- Use **Title Case** (capitalize first letter of each major word)
- Keep titles under 80 characters when possible
- ✅ `Skill — Python Automation`
- ❌ `python automation skill`

### Tags

- Use **lowercase-hyphen** format: `#deep-dive`, `#decision-making`, `#finance`
- Reuse existing tags before creating new ones
- **Limit 3-5 tags per entry; max 5 enforced by system**
- Examples: `#learning`, `#framework`, `#high-priority`, `#needs-decision`

### Dates

- Use ISO format: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM`
- Capture date when created; update when modified
- Include timezone if relevant (default: your local tz)

---

## Anti-Mess Guardrails

### Entry Hygiene Rules

1. **No empty status** — every entry must have defined status
2. **No orphan entry** — every entry should relate to at least one other item over time
3. **No duplicate titles** — search before creating
4. **Titles must be descriptive** — avoid vague titles like "Note" or "Idea"
5. **No stale statuses** — "Reading" entries shouldn't persist 6+ months

### Weekly Maintenance (15 minutes)

- Fix any missing Status fields
- Merge duplicate tags (e.g., #learning and #learn → #learning)
- Archive drafts older than 60 days with no progress

### Monthly Cleanup (30 minutes)

- Review all items with no update in 90+ days
- Promote useful Thoughts into Terms or Frameworks
- Verify all Relations still point to active entries
- Consolidate overly specific tags back to standard set

### Quarterly Review (1 hour)

- Finalize all "Ready to Publish" entries
- Review low-confidence items: study more, accept, or archive
- Reflect: which topics gained depth? which are obsolete?
- Adjust Priority and Type assignments based on current goals

---

## Visual Styling Choices

### Markdown Structure

- Use **H2** (`##`) for main page sections
- Use **H3** (`###`) only when absolutely necessary
- Use **bullets** for meaning; use **toggles** only for long reference material

### Formatting

- Use **bold** only for emphasized key terms (not entire sentences)
- Use callouts (or clear warning blocks) only for warnings, decisions, or next actions
- Keep emojis minimal and semantic: one icon per database type max

### Tables & Lists

- Use tables to compare options
- Use numbered lists for sequences (steps, priorities)
- Use bullets for related items, not priorities

---

## Summary

This standard keeps your library **scannable, linked, and fresh**:

- **Scannable**: consistent field order + short summaries make quick lookup easy
- **Linked**: relations connect related ideas so patterns emerge
- **Fresh**: regular maintenance prevents information decay

Apply to new entries immediately. Migrate legacy entries during weekly cleanup sessions.

For enforcement code, see `src/core/libraries.py` formatting functions.
