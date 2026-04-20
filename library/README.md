# Library Folder

This folder is the canonical Stage 9 personal library store.

From this point onward, the term "library" in this repo means the local `library/` folder, not Notion databases.

## Structure

- `library/profile/` — skills, interests, domains, learning priorities, focus themes
- `library/terms/` — concepts and definitions
- `library/books/` — book entries and updates
- `library/articles/` — article captures and insights
- `library/thoughts/` — draft thoughts and thought updates
- `library/references/` — reference materials (including formatting guide)
- `library/research/` — deep research bundles for "add to library" / "add to my personal knowledge" captures

## File Format

Entries are stored as Markdown files with front matter-like metadata and body content.
The library also maintains `library/index.json` as a generated retrieval index for search and bundle lookup commands.

Research bundles are stored as folders containing:

- `index.md` — categorized overview and why it matters
- `01-raw-input.md` — original input exactly as received
- `02-search-history.md` — search scope, matches, and research mode
- `03-research-notes.md` — synthesized research notes
- `04-information-to-track.md` — the most valuable data points to monitor
- `05-qa-log.md` — question/answer reasoning log
- `06-logic-trail.md` — decision and reasoning trail
- `07-conclusion.md` — conclusion and open questions

## Naming

`YYYYMMDD-HHMMSS-<slug>.md`

This keeps entries sortable by capture time and avoids filename collisions.

For research bundles, the parent folder uses the same timestamp + slug pattern.

## Retrieval Commands

- `search library: <query>` — search indexed library entries and bundles
- `library bundle: <topic>` — find matching research bundles
- `summarize library: <topic>` — read the matched bundle overview and tracking points
