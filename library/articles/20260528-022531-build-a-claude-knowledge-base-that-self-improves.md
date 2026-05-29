---
title: Build A Claude Knowledge Base That Self-Improves!
section: article
status: to-read
tags: [youtube, link, to-read]
captured_at: 2026-05-28T02:25
source_url: https://www.youtube.com/watch?v=ib74sLgjIBM
---

---
title: Build A Claude Knowledge Base That Self-Improves!
section: article
status: to-read
tags: [youtube, link, to-read]
captured_at: 2026-05-28T02:25
source_url: https://www.youtube.com/watch?v=ib74sLgjIBM
---

Source: https://www.youtube.com/watch?v=ib74sLgjIBM

Author: Systems Made Better

This video by the channel **Systems Made Better** details how to build a self-improving personal knowledge base (a "second brain") using Claude. Inspired by a setup shared by AI researcher Andrej Karpathy, this system relies entirely on simple local text files and folders instead of heavy databases, code, or complex plugins.

Here is the comprehensive summary and breakdown of the architecture, workflow, and maintenance loop.

---

## 🏗️ The System Architecture

The entire setup lives locally on your computer. It requires no vector databases, no Retrieval-Augmented Generation (RAG) embeddings, and no specialized software like Obsidian. It consists of **one configuration file** and **three distinct folders**:

* **`claude.md` (The Schema):** A markdown file sitting at the root folder. It serves as the "librarian handbook," instructing Claude exactly how to read, organize, navigate, and maintain the knowledge base.
* **`raw/` (The Capture Folder):** Act like a "junk drawer." This is where you dump unorganized notes, clippings, articles, screenshots, meeting transcripts, or book quotes. No organization or tagging is required by you.
* **`wiki/` (The Organized Core):** The AI librarian handles this folder exclusively. Claude reads the `raw/` files and populates the `wiki/` directory with organized, thematic markdown files and a centralized `index.md` file that acts as a map.
* **`outputs/` (The Action Results):** When you ask the system questions, create briefs, or request summaries, the resulting generated reports are saved automatically here.

---

## 🔄 The 5-Step Continuous Improvement Framework

The strength of the system comes from a compounding loop. As you interact with it, it continuously refines itself.

```
[1. Setup Structure] ➔ [2. Dump Raw Data] ➔ [3. AI Builds Wiki] ➔ [4. Query & Save Output] ➔ [5. Monthly Health Check] 🔁 Loops back to refine the Wiki

```

### 1. Structure Setup

Create the root directory on your machine (e.g., `Productivity Knowledge Base`) and add the `raw`, `wiki`, and `outputs` folders along with your foundational `claude.md` instructions.

### 2. The Raw Data Dump

Gather existing information and drop it into `raw/`. You can copy-paste text, utilize local markdown files, save images, or use browser extensions (like the Obsidian web clipper) to quickly turn web articles into clean markdown text.

### 3. Let the AI Build the Wiki

Point Claude to your folder structure and execute a single operational prompt:

> *"Read everything in RAW and compile a wiki in the wiki folder following the rules in your `claude.md`. Create the `index.md` first, then one markdown file per major topic and link related topics."*

Claude takes over the librarian role, generating structured topic pages, looking for hidden connections, and maintaining an index map. To prevent standard robotic AI phrasing, the video suggests providing Claude with an **Anti-AI Writing Style Guide** (modeled after Wikipedia style parameters).

### 4. Querying and Creating Outputs

When you need to solve a problem or learn something, start a chat session targeting your knowledge base. Because the generated reports map back into your `outputs/` folder, they can be re-ingested into the system later. This creates a compounding effect: *every question you ask makes the next answer more intelligent.*

### 5. The Monthly Health Check (Audit)

LLMs can occasionally introduce minor inaccuracies or hallucinate small details. To prevent these errors from compounding, run a monthly automated or manual health check script. The video demonstrates utilizing custom Claude instructions to execute a **7-Stage Audit Phase**:

1. **Contradictions:** Flag opposing viewpoints or clashing information between separate articles.
2. **Broken Backlinks:** Find dead or missing cross-references.
3. **Source Provenance:** Ensure facts are properly backed by text originally located in the `raw/` folder.
4. **Coverage Analysis:** Identify gaps where raw information hasn't been completely extracted.
5. **Stale Articles:** Flag entries older than 90 days that may need updating.
6. **Connection Discovery:** Surface thematic similarities between articles you haven't explicitly linked yet.
7. **New Article Recommendations:** Generate a menu of content ideas to build out next based on your current knowledge gaps.

---

## 💡 Key Takeaways & Considerations

* **Andrej Karpathy's Validation:** Large Language Models (LLMs) have large enough context windows to process substantial text volumes easily. Karpathy’s own personal knowledge base holds roughly 100 long-form articles (~400,000 words) processed perfectly fine by an LLM without needing complex indexing databases.
* **The 100-Day Compound Asset:** On Day 1, your knowledge base is just a collection of old notes. By Day 100, because it catalogs your unique reading material, meeting transcripts, and specific insights, it transforms into a highly proprietary asset that can serve as a specialized backend for a custom AI agent.
* **Token / Credit Management:** Running full-scale wiki builds and deep monthly health checks requires high token usage (the video mentions using roughly 45% of a session capacity on a Claude Max tier plan). To optimize costs, perform complete audits only **once a month** and space them out if you maintain multiple knowledge bases.

Provider Name: YouTube

Type: video

Captured At: 2026-05-28T02:25

