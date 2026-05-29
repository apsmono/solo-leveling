"""
Stage 9 personal library command handlers.

This module handles lightweight capture and lookup flows for:
  - Knowledge profile (skills, interests, domains)
  - Terms
  - Books
  - Articles
  - Thoughts
  - Library review summary

Current implementation stores captures as markdown files under library/.
This keeps Stage 9 local-first and file-based for predictable versioning.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
import json
import logging
from pathlib import Path
import re
from time import time
from typing import Any, Optional

from src.agents.dispatcher import run_agent
from src.core.config import SIGNAL_OWNER_ID, SIGNAL_POSTGRES_DSN, USE_FIRESTORE_LIBRARY
from src.core.library_store import _FileLibraryStore, _FirestoreLibraryStore, _LibraryStore
from src.integrations.web_fetch import fetch_url_metadata
from src.integrations.youtube import extract_video_id, fetch_transcript


logger = logging.getLogger(__name__)


class SearchCache:
    """
    In-memory LRU cache for library search queries with TTL.

    - Max 1000 cached entries (≈10MB memory)
    - 5-minute TTL per entry
    - Automatic expiration on access
    - No external dependencies
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.cache: dict[tuple[str, int], list[dict[str, Any]]] = {}
        self.timestamps: dict[tuple[str, int], float] = {}

    def get(self, key: tuple[str, int]) -> Optional[list[dict[str, Any]]]:
        """Retrieve cached value if exists and not expired."""
        if key in self.cache:
            age = time() - self.timestamps[key]
            if age < self.ttl:
                return self.cache[key]
            else:
                # Expired, remove
                del self.cache[key]
                del self.timestamps[key]
                return None
        return None

    def set(self, key: tuple[str, int], value: list[dict[str, Any]]) -> None:
        """Store value in cache, evicting oldest if at capacity."""
        if len(self.cache) >= self.max_size:
            # Evict least recently used (oldest timestamp)
            oldest_key = min(self.timestamps, key=self.timestamps.get)
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]

        self.cache[key] = value
        self.timestamps[key] = time()

    def invalidate(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
        self.timestamps.clear()


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LIBRARY_ROOT = _PROJECT_ROOT / "library"
_INDEX_PATH = _LIBRARY_ROOT / "index.json"
_SECTION_DIRS = {
    "profile": "profile",
    "term": "terms",
    "book": "books",
    "article": "articles",
    "thought": "thoughts",
    "reference": "references",
    "research": "research",
}


ALLOWED_PROFILE_TYPES = {"skill", "interest", "domain", "learning", "focus"}
ALLOWED_CONFIDENCE = {"high", "medium", "low", "exploring"}
ALLOWED_PRIORITY = {"now", "next", "later"}

_SENSITIVE_TOKENS = (
    "password",
    "secret",
    "api key",
    "token",
    "passport",
    "ktp",
    "identity number",
    "contact",
    "credit card",
    "bank account",
)

# Global search cache instance
_search_cache = SearchCache(max_size=1000, ttl_seconds=300)

# Module-level store singleton (refreshed on each access to handle test patches)
_library_store: _LibraryStore | None = None


def _get_store() -> _LibraryStore:
    """Return the current library store instance."""
    global _library_store
    if USE_FIRESTORE_LIBRARY:
        _library_store = _FirestoreLibraryStore(
            project_root=_PROJECT_ROOT,
            library_root=_LIBRARY_ROOT,
            index_path=_INDEX_PATH,
        )
    else:
        _library_store = _FileLibraryStore(
            project_root=_PROJECT_ROOT,
            library_root=_LIBRARY_ROOT,
            index_path=_INDEX_PATH,
        )
    return _library_store


def _ensure_library_dirs() -> None:
    _get_store()._ensure_library_dirs()


def _build_library_index() -> dict[str, Any]:
    return _get_store().build_index()


def _load_library_index() -> dict[str, Any]:
    return _get_store().load_index()


def _match_index_records(records: list[dict[str, Any]], query: str, limit: int = 8) -> list[dict[str, Any]]:
    return _FileLibraryStore._match_index_records(records, query, limit)


def _find_bundle_by_query(query: str, limit: int = 5) -> list[dict[str, Any]]:
    return _get_store().find_bundles(query, limit=limit)


def _find_entries_by_query(query: str, limit: int = 8) -> list[dict[str, Any]]:
    cache_key = (query, limit)

    # Check cache first
    cached = _search_cache.get(cache_key)
    if cached is not None:
        return cached

    # Cache miss: search via store
    results = _get_store().search_entries(query, limit=limit)

    # Store in cache for future calls
    _search_cache.set(cache_key, results)
    return results


def _extract_summary_from_bundle(bundle_path: str) -> str:
    return _get_store().get_bundle_summary(bundle_path)


def _resolve_section_dir(section: str) -> str:
    return _get_store()._resolve_section_dir(section)


def _fire_embedding_hook(
    entry_id: str,
    markdown_text: str,
    section: str,
    source_url: Optional[str] = None,
) -> None:
    """Fire the vector embedding hook asynchronously if the event loop is running."""
    if not SIGNAL_POSTGRES_DSN:
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop — sync context (tests, scripts). Skip silently.
        return

    try:
        from src.vector.hooks import on_entry_saved

        loop.create_task(
            on_entry_saved(
                entry_id=entry_id,
                text=markdown_text,
                section=section,
                owner_id=SIGNAL_OWNER_ID,
                source_url=source_url,
            )
        )
    except Exception:
        logger.warning("Failed to schedule embedding hook", exc_info=True)


def _capture_entry(
    section: str,
    title: str,
    body: str,
    *,
    status: str = "draft",
    tags: list[str] | None = None,
    source_url: Optional[str] = None,
) -> str:
    result = _get_store().save_entry(
        section=section,
        title=title,
        body=body,
        status=status,
        tags=tags,
        source_url=source_url,
    )
    _search_cache.invalidate()  # Clear cache on new entry

    # Fire vector embedding hook asynchronously
    _fire_embedding_hook(
        entry_id=Path(result).stem,
        markdown_text=body,
        section=section,
        source_url=source_url,
    )
    return result


def _search_entries(section: str, query: str, limit: int = 8) -> list[str]:
    results = _get_store().search_all_entries(query, limit=limit)
    # Filter to section
    dirname = _resolve_section_dir(section)
    prefix = f"library/{dirname}/"
    return [r for r in results if r.startswith(prefix)]


def _count_entries(section: str) -> int:
    return _get_store().count_entries(section)


def _recent_entries(section: str, limit: int = 10) -> list[str]:
    return _get_store().recent_entries(section, limit)


def _search_all_entries(query: str, limit: int = 12) -> list[str]:
    return _get_store().search_all_entries(query, limit)


def handle_library_command(text: str, intent: str) -> str:
    """Route library command to the right handler."""
    if intent == "library_capture":
        return _handle_library_capture(text)
    if intent == "library_search":
        return _handle_library_search(text)
    if intent == "library_bundle":
        return _handle_library_bundle(text)
    if intent == "library_summary":
        return _handle_library_summary(text)
    if intent == "library_profile":
        return _handle_profile(text)
    if intent == "library_term":
        return _handle_term(text)
    if intent == "library_book":
        return _handle_book(text)
    if intent == "library_article":
        return _handle_article(text)
    if intent == "library_thought":
        return _handle_thought(text)
    if intent == "library_review":
        return _handle_review(text)
    if intent == "library_maintenance":
        return format_library_maintenance_summary()
    if intent == "library_guide":
        return _save_formatting_guide_to_library()
    return "Library command not recognized."


def _contains_sensitive_content(text: str) -> bool:
    lower = text.lower()
    return any(token in lower for token in _SENSITIVE_TOKENS)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug[:80] or "entry"


def _normalize_tags(values: list[str]) -> list[str]:
    tags = []
    for value in values:
        tag = _slugify(str(value))
        if tag:
            tags.append(tag)
    return tags[:5]


def _normalize_str_list(value: object) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, str) and item.strip():
                result.append(item.strip())
        return result
    return []


def _normalize_qa_list(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, str]] = []
    for item in value:
        if isinstance(item, dict):
            question = str(item.get("question", "")).strip()
            answer = str(item.get("answer", "")).strip()
            if question or answer:
                items.append({"question": question, "answer": answer})
    return items


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\n", "", cleaned)
        cleaned = re.sub(r"\n```$", "", cleaned)
    return cleaned.strip()


def _default_capture_analysis(payload: str, existing_matches: list[str]) -> dict:
    lower = payload.lower()
    words = payload.split()

    if "http://" in lower or "https://" in lower:
        meta = fetch_url_metadata(payload.strip())
        platform = meta.get("platform", "generic")
        category = "article"
        storage_folder = "articles"
        item_type = f"{platform}-research" if platform != "generic" else "article-research"
        title = meta.get("title") or f"Article Research — {payload[:60].strip()}"
        information_to_track = [
            "source-url",
            "author-or-source",
            "core-claim",
            "key-supporting-points",
            "why-it-matters",
            "follow-up-action",
        ]
        if platform == "youtube":
            information_to_track.extend(["video-transcript", "channel", "duration"])
        elif platform == "github":
            information_to_track.extend(["repo-language", "stars", "use-case"])
        summary = meta.get("description") or meta.get("title") or payload.strip()
        why_valuable = f"External {platform} resource flagged for long-term development and reference."
        key_facts = [f"Source: {payload.strip()}"]
        if meta.get("author"):
            key_facts.append(f"Author: {meta['author']}")
        if meta.get("extra"):
            for k, v in meta["extra"].items():
                if v and k not in ("thumbnail_url", "thumbnail_width", "thumbnail_height"):
                    key_facts.append(f"{k.replace('_', ' ').title()}: {v}")
        return {
            "title": title,
            "category": category,
            "storage_folder": storage_folder,
            "item_type": item_type,
            "summary": summary,
            "why_valuable": why_valuable,
            "key_facts": key_facts,
            "information_to_track": information_to_track,
            "research_notes": [
                "Captured from external URL.",
                "Metadata fetched automatically where available.",
                "Further external verification may still be useful.",
            ],
            "qa_log": [
                {
                    "question": "What is the most important thing to preserve from this intake?",
                    "answer": "The original source URL, fetched metadata, and any extracted insights for later reuse.",
                }
            ],
            "logic_trail": [
                "Detect URL in input and identify platform.",
                "Fetch metadata via platform-specific API (oEmbed, GitHub API, or HTML parsing).",
                "Search existing library entries to avoid duplication.",
                "Choose the storage folder that best matches long-term retrieval needs.",
            ],
            "conclusion": "Store this as a reusable knowledge asset and revisit it as new evidence or decisions appear.",
            "tags": _normalize_tags([category, item_type, platform, "critical-knowledge"]),
            "open_questions": [
                "What must be validated externally?",
                "What action should this knowledge change?",
            ],
            "research_mode": "url-enriched",
            "related_existing_entries": existing_matches[:5],
            "source_url": payload.strip(),
        }
    elif lower.startswith("book") or " by " in lower:
        category = "book"
        storage_folder = "books"
        item_type = "book-research"
        title = f"Book Research — {payload[:60].strip()}"
        information_to_track = [
            "author",
            "main-thesis",
            "top-insights",
            "use-cases",
            "rating-criteria",
            "next-action",
        ]
    elif len(words) <= 6 and "=" not in payload:
        category = "term"
        storage_folder = "terms"
        item_type = "concept"
        title = f"Concept Research — {payload.strip()}"
        information_to_track = [
            "plain-definition",
            "why-it-matters",
            "example",
            "related-concepts",
            "review-cadence",
        ]
    else:
        category = "research"
        storage_folder = "research"
        item_type = "knowledge-intake"
        title = f"Knowledge Intake — {payload[:60].strip()}"
        information_to_track = [
            "core-definition",
            "decision-relevance",
            "high-value-facts",
            "open-questions",
            "next-actions",
            "related-topics",
        ]

    return {
        "title": title,
        "category": category,
        "storage_folder": storage_folder,
        "item_type": item_type,
        "summary": payload.strip(),
        "why_valuable": "This topic was explicitly flagged for long-term development, so it should be captured with reasoning, traceability, and follow-up points.",
        "key_facts": [payload.strip()],
        "information_to_track": information_to_track,
        "research_notes": [
            "Captured from explicit user request.",
            "Existing library entries were checked for overlap before writing.",
            "Further external verification may still be useful for factual topics.",
        ],
        "qa_log": [
            {
                "question": "What is the most important thing to preserve from this intake?",
                "answer": "The original framing, the category choice, the facts to track, and the conclusion for later reuse.",
            }
        ],
        "logic_trail": [
            "Inspect the input for obvious type cues such as URL, term-style query, or book pattern.",
            "Search existing library entries to avoid duplication and recover context.",
            "Choose the storage folder that best matches long-term retrieval needs.",
            "Capture both raw input and processed synthesis so nothing important is lost.",
        ],
        "conclusion": "Store this as a reusable knowledge asset and revisit it as new evidence or decisions appear.",
        "tags": _normalize_tags([category, item_type, "critical-knowledge"]),
        "open_questions": [
            "What must be validated externally?",
            "What action should this knowledge change?",
        ],
        "research_mode": "fallback-heuristic",
        "related_existing_entries": existing_matches[:5],
        "source_url": None,
    }


def _parse_capture_analysis(response: str, payload: str, existing_matches: list[str]) -> dict:
    fallback = _default_capture_analysis(payload, existing_matches)
    try:
        parsed = json.loads(_strip_code_fences(response))
    except Exception:
        return fallback

    title = str(parsed.get("title", fallback["title"]))[:120].strip() or fallback["title"]
    category = _slugify(str(parsed.get("category", fallback["category"]))) or fallback["category"]
    storage_folder = _slugify(str(parsed.get("storage_folder", parsed.get("category", fallback["storage_folder"])))) or fallback["storage_folder"]
    item_type = _slugify(str(parsed.get("item_type", fallback["item_type"]))) or fallback["item_type"]

    return {
        "title": title,
        "category": category,
        "storage_folder": storage_folder,
        "item_type": item_type,
        "summary": str(parsed.get("summary", fallback["summary"])).strip() or fallback["summary"],
        "why_valuable": str(parsed.get("why_valuable", fallback["why_valuable"])).strip() or fallback["why_valuable"],
        "key_facts": _normalize_str_list(parsed.get("key_facts")) or fallback["key_facts"],
        "information_to_track": _normalize_str_list(parsed.get("information_to_track")) or fallback["information_to_track"],
        "research_notes": _normalize_str_list(parsed.get("research_notes")) or fallback["research_notes"],
        "qa_log": _normalize_qa_list(parsed.get("qa_log")) or fallback["qa_log"],
        "logic_trail": _normalize_str_list(parsed.get("logic_trail")) or fallback["logic_trail"],
        "conclusion": str(parsed.get("conclusion", fallback["conclusion"])).strip() or fallback["conclusion"],
        "tags": _normalize_tags(_normalize_str_list(parsed.get("tags")) or fallback["tags"]),
        "open_questions": _normalize_str_list(parsed.get("open_questions")) or fallback["open_questions"],
        "research_mode": "ai-synthesized",
        "related_existing_entries": existing_matches[:5],
        "source_url": fallback.get("source_url"),
    }


def _analyze_capture_request(payload: str, existing_matches: list[str]) -> dict:
    context = (
        f"Original request:\n{payload}\n\n"
        f"Existing matching library entries:\n"
        + ("\n".join(f"- {item}" for item in existing_matches) if existing_matches else "- none")
    )
    task = (
        "Analyze this knowledge intake for long-term storage. Return valid JSON only with keys: "
        "title, category, storage_folder, item_type, summary, why_valuable, key_facts, "
        "information_to_track, research_notes, qa_log, logic_trail, conclusion, tags, open_questions. "
        "qa_log must be an array of objects with question and answer. "
        "Optimize for durable knowledge capture, retrieval, and future decision-making."
    )
    system = (
        "You are a research librarian for a personal knowledge system. "
        "Categorize incoming information, identify the most valuable facts to preserve, "
        "and produce structured outputs for a filesystem-based library. "
        "Return strict JSON only."
    )
    try:
        response = run_agent(task=task, context=context, system=system)
        return _parse_capture_analysis(response, payload, existing_matches)
    except Exception as exc:
        logger.warning("Deep library capture fell back to heuristic analysis: %s", exc)
        return _default_capture_analysis(payload, existing_matches)


def _write_bundle_file(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _capture_research_bundle(payload: str, analysis: dict, existing_matches: list[str]) -> str:
    _ensure_library_dirs()
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    section_dir = _resolve_section_dir(analysis["storage_folder"])
    bundle_dir = _LIBRARY_ROOT / section_dir / f"{ts}-{_slugify(analysis['title'])}"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    source_url = analysis.get("source_url")
    source_url_line = f"source_url: {source_url}\n" if source_url else ""

    metadata = (
        f"---\n"
        f"title: {analysis['title']}\n"
        f"category: {analysis['category']}\n"
        f"storage_folder: {section_dir}\n"
        f"item_type: {analysis['item_type']}\n"
        f"tags: [{', '.join(analysis['tags'])}]\n"
        f"captured_at: {datetime.now().isoformat(timespec='minutes')}\n"
        f"research_mode: {analysis['research_mode']}\n"
        f"{source_url_line}"
        f"---\n\n"
    )

    overview = metadata + (
        f"## Summary\n\n{analysis['summary']}\n\n"
        f"## Why This Is Valuable\n\n{analysis['why_valuable']}\n\n"
        "## Key Facts\n\n"
        + "\n".join(f"- {item}" for item in analysis["key_facts"])
        + "\n\n## Information To Track\n\n"
        + "\n".join(f"- {item}" for item in analysis["information_to_track"])
        + "\n\n## Related Existing Entries\n\n"
        + ("\n".join(f"- {item}" for item in analysis["related_existing_entries"]) if analysis["related_existing_entries"] else "- none")
        + "\n"
    )

    search_history = metadata + (
        "## Search History\n\n"
        f"- Original query: {payload}\n"
        f"- Search mode: {analysis['research_mode']}\n"
        "- Library scan: searched existing markdown entries under library/ for related material\n"
        + ("\n".join(f"- Existing match: {item}" for item in existing_matches) if existing_matches else "- Existing match: none")
        + "\n"
    )

    research_notes = metadata + "## Research Notes\n\n" + "\n".join(f"- {item}" for item in analysis["research_notes"]) + "\n"
    tracking = metadata + "## Valuable Information To Track\n\n" + "\n".join(f"- {item}" for item in analysis["information_to_track"]) + "\n"
    qa_lines = []
    for item in analysis["qa_log"]:
        qa_lines.append(f"### Q: {item['question'] or '(unspecified)'}\n\n{item['answer'] or '(no answer)'}\n")
    qa_log = metadata + "## Question / Answer Log\n\n" + ("\n".join(qa_lines) if qa_lines else "No Q/A generated.\n")
    logic = metadata + "## Logic Trail\n\n" + "\n".join(f"- {item}" for item in analysis["logic_trail"]) + "\n"
    conclusion = metadata + (
        f"## Conclusion\n\n{analysis['conclusion']}\n\n"
        "## Open Questions\n\n"
        + "\n".join(f"- {item}" for item in analysis["open_questions"])
        + "\n"
    )
    raw_input = metadata + f"## Raw Input\n\n{payload}\n"

    _write_bundle_file(bundle_dir / "index.md", overview)
    _write_bundle_file(bundle_dir / "01-raw-input.md", raw_input)
    _write_bundle_file(bundle_dir / "02-search-history.md", search_history)
    _write_bundle_file(bundle_dir / "03-research-notes.md", research_notes)
    _write_bundle_file(bundle_dir / "04-information-to-track.md", tracking)
    _write_bundle_file(bundle_dir / "05-qa-log.md", qa_log)
    _write_bundle_file(bundle_dir / "06-logic-trail.md", logic)
    _write_bundle_file(bundle_dir / "07-conclusion.md", conclusion)

    # If YouTube URL, fetch and save transcript
    if source_url and "youtube" in analysis.get("item_type", ""):
        video_id = extract_video_id(source_url)
        if video_id:
            transcript = fetch_transcript(video_id)
            if transcript:
                transcript_content = (
                    f"---\n"
                    f"title: Transcript: {analysis['title']}\n"
                    f"category: transcript\n"
                    f"tags: [transcript, youtube]\n"
                    f"captured_at: {datetime.now().isoformat(timespec='minutes')}\n"
                    f"{source_url_line}"
                    f"---\n\n"
                    f"{transcript}\n"
                )
                _write_bundle_file(bundle_dir / "08-transcript.md", transcript_content)

    # Auto-produce supporting entries for every deep capture:
    # 1. Term definition in library/terms/
    _capture_entry(
        "term",
        f"Term: {analysis['title']}",
        (
            f"## Definition\n\n{analysis['summary']}\n\n"
            "## Key Facts\n\n"
            + "\n".join(f"- {item}" for item in analysis["key_facts"])
            + "\n\n## Information To Track\n\n"
            + "\n".join(f"- {item}" for item in analysis["information_to_track"])
        ),
        status="active",
        tags=analysis["tags"],
        source_url=source_url,
    )

    # 2. Reference file in library/references/
    _capture_entry(
        "reference",
        f"Reference: {analysis['title']}",
        (
            f"## Overview\n\n{analysis['summary']}\n\n"
            f"## Why This Is Valuable\n\n{analysis['why_valuable']}\n\n"
            "## Research Notes\n\n"
            + "\n".join(f"- {item}" for item in analysis["research_notes"])
            + "\n\n## Open Questions\n\n"
            + "\n".join(f"- {item}" for item in analysis["open_questions"])
            + f"\n\n## Source Bundle\n\n{str(bundle_dir.relative_to(_PROJECT_ROOT))}\n"
        ),
        status="active",
        tags=analysis["tags"],
        source_url=source_url,
    )

    # 3. Thought entry in library/thoughts/ (reasoning + conclusion)
    logic_text = "\n".join(f"- {item}" for item in analysis["logic_trail"])
    _capture_entry(
        "thought",
        f"Research Reasoning: {analysis['title']}",
        (
            "## Thought Process\n\n"
            + logic_text
            + f"\n\n## Conclusion\n\n{analysis['conclusion']}\n\n"
            "## Open Questions\n\n"
            + "\n".join(f"- {item}" for item in analysis["open_questions"])
            + f"\n\n## Source Bundle\n\n{str(bundle_dir.relative_to(_PROJECT_ROOT))}\n"
        ),
        status="draft",
        tags=analysis["tags"],
        source_url=source_url,
    )

    _build_library_index()

    return str(bundle_dir.relative_to(_PROJECT_ROOT))


def _handle_library_search(text: str) -> str:
    query = _extract_after_prefix(text, ("search library:", "find in library:", "library search:", "search library ", "find in library ", "library search ")).strip()
    if not query:
        return "Use: search library: <query>"
    results = _find_entries_by_query(query, limit=10)
    if not results:
        return f"No library matches found for: {query}"
    lines = [f"Library matches for '{query}':\n"]
    for idx, item in enumerate(results, 1):
        lines.append(f"{idx}. {item['title']}")
        path = item["path"]
        if item.get("type") == "bundle-index":
            path = path.rsplit("/", 1)[0]
        lines.append(f"   {path}")
    return "\n".join(lines)


def _handle_library_bundle(text: str) -> str:
    query = _extract_after_prefix(text, ("library bundle:", "research bundle:", "open bundle:", "open research:", "library bundle ", "research bundle ", "open bundle ", "open research ")).strip()
    if not query:
        return "Use: library bundle: <topic>"
    bundles = _find_bundle_by_query(query, limit=5)
    if not bundles:
        return f"No research bundle found for: {query}"
    lines = [f"Research bundles for '{query}':\n"]
    for idx, bundle in enumerate(bundles, 1):
        lines.append(f"{idx}. {bundle['title']}")
        lines.append(f"   {bundle['path']}")
    return "\n".join(lines)


def _handle_library_summary(text: str) -> str:
    query = _extract_after_prefix(text, ("summarize library:", "summarise library:", "summarize research:", "summarise research:", "library summary:", "summarize library ", "summarise library ", "summarize research ", "summarise research ", "library summary ")).strip()
    if not query:
        return "Use: summarize library: <topic>"
    bundles = _find_bundle_by_query(query, limit=1)
    if bundles:
        bundle = bundles[0]
        return (
            f"Summary for '{query}':\n"
            f"{bundle['path']}\n\n"
            f"{_extract_summary_from_bundle(bundle['path'])}"
        )

    entries = _find_entries_by_query(query, limit=3)
    if not entries:
        return f"No library summary source found for: {query}"
    lines = [f"Top library matches for '{query}':\n"]
    for idx, entry in enumerate(entries, 1):
        lines.append(f"{idx}. {entry['title']}")
        lines.append(f"   {entry['path']}")
    return "\n".join(lines)


def _handle_library_capture(text: str) -> str:
    lower = text.lower().strip()
    payload = _extract_after_prefix(
        text,
        (
            "add to library:",
            "add to my personal knowledge:",
            "add to library ",
            "add to my personal knowledge ",
        ),
    )

    if not payload:
        return (
            "Use: add to library: <topic, note, question, source, or raw information>\n"
            "I will categorize it, define what is valuable to track, and save a full research bundle into library/."
        )

    if _contains_sensitive_content(text):
        return "Library capture blocked because the input appears to contain sensitive secrets or identity data."

    existing_matches = _search_all_entries(payload, limit=8)
    analysis = _analyze_capture_request(payload, existing_matches)
    bundle_path = _capture_research_bundle(payload, analysis, existing_matches)

    return (
        "Knowledge capture saved to local library.\n"
        f"Category: {analysis['category']}\n"
        f"Storage: {bundle_path}\n"
        f"Track next: {', '.join(analysis['information_to_track'][:4])}"
    )


def _extract_after_prefix(text: str, prefixes: tuple[str, ...]) -> str:
    lower = text.lower().strip()
    for prefix in prefixes:
        if lower.startswith(prefix):
            return text.strip()[len(prefix):].strip()
    return ""


def _handle_profile(text: str) -> str:
    lower = text.lower().strip()

    if _contains_sensitive_content(text):
        return (
            "Profile capture blocked: this command appears to include sensitive data.\n"
            "Allowed scope is knowledge profile only (skills, interests, domains, learning priorities, focus themes)."
        )

    if lower.startswith("profile summary"):
        rows = _recent_entries("profile", limit=10)
        if not rows:
            return "No profile entries found yet. Try: profile skill: python | confidence: high | priority: now"

        lines = ["Recent profile entries:\n"]
        for idx, row in enumerate(rows, 1):
            lines.append(f"{idx}. {row}")
        return "\n".join(lines)

    payload = _extract_after_prefix(text, ("profile skill:", "profile interest:", "profile domain:", "profile learning:", "profile focus:"))

    profile_type = ""
    for candidate in ALLOWED_PROFILE_TYPES:
        marker = f"profile {candidate}:"
        if lower.startswith(marker):
            profile_type = candidate
            break

    if payload and profile_type:
        confidence = _extract_field(lower, "confidence")
        priority = _extract_field(lower, "priority")

        if confidence and confidence not in ALLOWED_CONFIDENCE:
            return "Invalid confidence. Use: high, medium, low, or exploring."
        if priority and priority not in ALLOWED_PRIORITY:
            return "Invalid priority. Use: now, next, or later."

        title = f"Profile: {profile_type.title()} - {payload.split('|')[0].strip()}"
        body = (
            f"Type: {profile_type}\n"
            f"Input: {payload}\n"
            f"Captured At: {datetime.now().isoformat(timespec='minutes')}"
        )
        formatted = _apply_formatting_standard("profile", title, body, metadata={"status": "active"})
        path = _capture_entry("profile", formatted["title"], formatted["body"], status=formatted["status"], tags=formatted["tags"])
        return f"Profile item saved to local library.\n{path}"

    if lower.startswith("profile update:"):
        item = text.split(":", 1)[1].strip() if ":" in text else ""
        if not item:
            return "Use: profile update: <item> | <new value>"
        title = f"Profile Update: {item.split('|')[0].strip()}"
        body = f"Update: {item}\nCaptured At: {datetime.now().isoformat(timespec='minutes')}"
        path = _capture_entry("profile", title, body, status="updated")
        return f"Profile update saved to local library.\n{path}"

    return (
        "Profile command not recognized.\n"
        "Try:\n"
        "• profile skill: python | confidence: high | priority: now\n"
        "• profile interest: personal knowledge systems | priority: next\n"
        "• profile domain: finance | focus: cashflow planning\n"
        "• profile update: python skill | moved to advanced\n"
        "• profile summary"
    )


def _handle_term(text: str) -> str:
    lower = text.lower().strip()

    if lower.startswith("add term:"):
        payload = text.split(":", 1)[1].strip() if ":" in text else ""
        if not payload:
            return "Use: add term: <term> = <definition>"
        if "=" not in payload:
            return "Use: add term: <term> = <definition>"
        term_title = payload.split("=", 1)[0].strip() if "=" in payload else payload
        definition = payload.split("=", 1)[1].strip() if "=" in payload else ""
        if not term_title or not definition:
            return "Use: add term: <term> = <definition>"
        body = f"{payload}\nCaptured At: {datetime.now().isoformat(timespec='minutes')}"
        formatted = _apply_formatting_standard("term", f"Term: {term_title}", body, metadata={"status": "active"})
        path = _capture_entry("term", formatted["title"], formatted["body"], status=formatted["status"], tags=formatted["tags"])
        return f"Term saved to local library.\n{path}"

    if lower.startswith("term ") or lower.startswith("define "):
        query = _extract_after_prefix(text, ("term ", "define ")).strip()
        if not query:
            return "Use: term <word>"
        results = _search_entries("term", query, limit=5)
        if not results:
            return f"No term result found for: {query}"
        lines = [f"Results for '{query}':\n"]
        for i, row in enumerate(results, 1):
            lines.append(f"{i}. {row}")
        return "\n".join(lines)

    return "Try: add term: <term> = <definition> or term <word>"


def _handle_book(text: str) -> str:
    lower = text.lower().strip()

    if lower.startswith("book:"):
        payload = text.split(":", 1)[1].strip() if ":" in text else ""
        if not payload:
            return "Use: book: <title> by <author>"
        if " by " not in payload.lower():
            return "Use: book: <title> by <author>"
        title = f"Book: {payload.split('|')[0].strip()}"
        body = f"{payload}\nStatus: wishlist\nCaptured At: {datetime.now().isoformat(timespec='minutes')}"
        formatted = _apply_formatting_standard("book", title, body, metadata={"status": "wishlist"})
        path = _capture_entry("book", formatted["title"], formatted["body"], status=formatted["status"], tags=formatted["tags"])
        return f"Book saved to local library.\n{path}"

    if lower.startswith("reading ") or lower.startswith("finished "):
        status = "reading" if lower.startswith("reading ") else "finished"
        name = _extract_after_prefix(text, ("reading ", "finished ")).strip()
        if not name:
            return "Use: reading <title> or finished <title>"
        path = _capture_entry("book", f"Book Update: {name}", f"Status: {status}\nCaptured At: {datetime.now().isoformat(timespec='minutes')}", status=status)
        return f"Book status update saved to local library.\n{path}"

    if lower.startswith("book insights:"):
        query = text.split(":", 1)[1].strip() if ":" in text else ""
        if not query:
            return "Use: book insights: <title>"
        results = _search_entries("book", query, limit=5)
        if not results:
            return f"No book insights found for: {query}"
        lines = [f"Book insights matches for '{query}':\n"]
        for i, row in enumerate(results, 1):
            lines.append(f"{i}. {row}")
        return "\n".join(lines)

    return "Try: book: <title> by <author>, reading <title>, finished <title>, or book insights: <title>"


def _handle_article(text: str) -> str:
    lower = text.lower().strip()

    if lower.startswith("article:"):
        lines = text.strip().splitlines()
        article_line = lines[0] if lines else ""
        payload = article_line.split(":", 1)[1].strip() if ":" in article_line else ""
        if not payload:
            return "Use: article: <url or title>"
        if len(payload) < 5:
            return "Use: article: <url or title>"

        # Parse optional tags, status, transcript flag, and notes from subsequent lines
        extra_tags: list[str] = []
        extra_status = "to-read"
        include_transcript = False
        user_notes = ""
        for line in lines[1:]:
            line_lower = line.lower().strip()
            if line_lower.startswith("tags:"):
                tag_str = line.split(":", 1)[1].strip()
                extra_tags = [t.strip() for t in tag_str.split(",") if t.strip()]
            elif line_lower.startswith("status:"):
                extra_status = line.split(":", 1)[1].strip()
            elif line_lower.startswith("transcript:"):
                tv = line.split(":", 1)[1].strip().lower()
                include_transcript = tv in ("true", "yes", "1")
            elif line_lower.startswith("notes:"):
                user_notes = line.split(":", 1)[1].strip()

        # Detect and enrich URLs
        stripped = payload.strip()
        if stripped.startswith("http://") or stripped.startswith("https://"):
            meta = fetch_url_metadata(stripped)
            title = meta.get("title") or stripped
            body_lines = [f"Source: {stripped}"]
            if meta.get("description"):
                body_lines.append(f"Description: {meta['description']}")
            if meta.get("author"):
                body_lines.append(f"Author: {meta['author']}")
            if meta.get("extra"):
                for k, v in meta["extra"].items():
                    if v and k not in ("thumbnail_url", "thumbnail_width", "thumbnail_height"):
                        body_lines.append(f"{k.replace('_', ' ').title()}: {v}")
            body_lines.append(f"Captured At: {datetime.now().isoformat(timespec='minutes')}")

            # Fetch YouTube transcript if requested
            platform = meta.get("platform", "article")
            if include_transcript and platform == "youtube":
                video_id = extract_video_id(stripped)
                if video_id:
                    transcript = fetch_transcript(video_id)
                    if transcript:
                        body_lines.append("\n## Transcript\n")
                        body_lines.append(transcript)
                    else:
                        body_lines.append("\n> Transcript unavailable for this video.\n")

            if user_notes:
                body_lines.append("\n## My Notes\n")
                body_lines.append(user_notes)

            body = "\n\n".join(body_lines)
            tags = [platform, "link", extra_status]
            if extra_tags:
                tags.extend(extra_tags)
            path = _capture_entry("article", title, body, status=extra_status, tags=tags, source_url=stripped)
            return f"Article saved to local library.\n{path}\nPlatform: {platform}"

        title = f"Article: {payload.split('|')[0].strip()}"
        body = f"{payload}\nCaptured At: {datetime.now().isoformat(timespec='minutes')}"
        formatted = _apply_formatting_standard("article", title, body, metadata={"status": extra_status})
        tags = formatted["tags"]
        if extra_tags:
            tags = list(dict.fromkeys(tags + extra_tags))
        path = _capture_entry("article", formatted["title"], formatted["body"], status=extra_status, tags=tags)
        return f"Article saved to local library.\n{path}"

    if lower.startswith("articles on "):
        topic = _extract_after_prefix(text, ("articles on ",)).strip()
        if not topic:
            return "Use: articles on <topic>"
        results = _search_entries("article", topic, limit=8)
        if not results:
            return f"No articles found for topic: {topic}"
        lines = [f"Articles on '{topic}':\n"]
        for i, row in enumerate(results, 1):
            lines.append(f"{i}. {row}")
        return "\n".join(lines)

    return "Try: article: <url> or articles on <topic>"


def _handle_thought(text: str) -> str:
    lower = text.lower().strip()

    if lower.startswith("thought:"):
        payload = text.split(":", 1)[1].strip() if ":" in text else ""
        if not payload:
            return "Use: thought: <idea>"
        if len(payload.strip()) < 8:
            return "Use: thought: <idea with enough detail to be useful>"
        title = f"Thought: {payload[:80].strip()}"
        body = f"{payload}\nStatus: draft\nCaptured At: {datetime.now().isoformat(timespec='minutes')}"
        formatted = _apply_formatting_standard("thought", title, body, metadata={"status": "draft"})
        path = _capture_entry("thought", formatted["title"], formatted["body"], status=formatted["status"], tags=formatted["tags"])
        return f"Thought saved to local library.\n{path}"

    if lower.startswith("draft:") or lower.startswith("publish thought:"):
        action = "draft lookup" if lower.startswith("draft:") else "publish"
        payload = text.split(":", 1)[1].strip() if ":" in text else ""
        if not payload:
            return "Use: draft: <title> or publish thought: <title>"
        path = _capture_entry(
            "thought",
            f"Thought Update: {payload}",
            f"Action: {action}\nCaptured At: {datetime.now().isoformat(timespec='minutes')}",
            status="updated",
        )
        return f"Thought update saved to local library.\n{path}"

    return "Try: thought: <idea>, draft: <title>, or publish thought: <title>"


def _handle_review(_: str) -> str:
    profile = _count_entries("profile")
    terms = _count_entries("term")
    books = _count_entries("book")
    articles = _count_entries("article")
    thoughts = _count_entries("thought")

    return (
        "Library quick review:\n"
        f"• Profile entries: {profile}\n"
        f"• Terms: {terms}\n"
        f"• Books: {books}\n"
        f"• Articles: {articles}\n"
        f"• Thoughts: {thoughts}\n\n"
        "Tip: run 'profile summary' or 'review terms' style searches for details."
    )


def format_library_maintenance_summary() -> str:
    profile = _count_entries("profile")
    terms = _count_entries("term")
    books = _count_entries("book")
    articles = _count_entries("article")
    thoughts = _count_entries("thought")
    references = _count_entries("reference")
    bundles = sum(1 for path in (_LIBRARY_ROOT / _resolve_section_dir("research")).iterdir() if path.is_dir()) if (_LIBRARY_ROOT / _resolve_section_dir("research")).exists() else 0

    lines = [
        "Weekly library maintenance",
        "",
        "Coverage:",
        f"• Profile: {profile}",
        f"• Terms: {terms}",
        f"• Books: {books}",
        f"• Articles: {articles}",
        f"• Thoughts: {thoughts}",
        f"• References: {references}",
        f"• Research bundles: {bundles}",
        "",
        "Checklist:",
        "• Review the newest research bundles and promote durable notes into core sections.",
        "• Clean weak titles, tags, or statuses in the latest captures.",
        "• Revisit unfinished books, unread articles, and draft thoughts.",
        "• Search for duplicates or overlapping entries before adding more.",
        "• Decide the next 1-3 topics that should move from capture to action.",
    ]
    return "\n".join(lines)


def _extract_field(lower_text: str, field: str) -> str:
    match = re.search(rf"\b{field}\s*:\s*([a-z-]+)", lower_text)
    return match.group(1).strip() if match else ""


def _apply_formatting_standard(
    library_type: str,
    title: str,
    body: str,
    metadata: dict | None = None
) -> dict:
    """
    Apply Stage 9 formatting standard to library entry.

    Enforces:
    - Title Case for titles
    - Consistent field order (9-field standard)
    - Tag validation (lowercase-hyphen, max 5)
    - Sensitive content blocking
    - Consistent date format

    Returns: {title, body, formatted_date, tags, library_type, status}
    """
    if not metadata:
        metadata = {}

    # Enforce title case
    title = _ensure_title_case(title)

    # Validate and normalize tags
    tags = metadata.get("tags", [])
    if tags:
        if isinstance(tags, str):
            tags = [t.strip().lower() for t in tags.split(",")]
        tags = [t.replace(" ", "-") for t in tags if t.strip()]
        tags = tags[:5]  # Enforce max 5 tags

    # Add timestamp
    formatted_date = metadata.get("date") or datetime.now().isoformat(timespec="minutes")

    return {
        "title": title,
        "body": body,
        "formatted_date": formatted_date,
        "tags": tags,
        "library_type": library_type,
        "status": metadata.get("status", "draft").lower(),
    }


def _ensure_title_case(text: str) -> str:
    """Convert text to Title Case, preserving acronyms (API, HTTP, MCP)."""
    words = text.split()
    result = []
    for word in words:
        if len(word) <= 2 or word.isupper():
            result.append(word)
        else:
            result.append(word.capitalize())
    return " ".join(result)


def _save_formatting_guide_to_library() -> str:
    """
    Save formatting guide as local reference markdown in library/references.
    Call via WhatsApp: "library guide" or directly from handlers.
    """
    guide_title = "Reference: Local Formatting Guide for Stage 9 Library"

    guide_body = (
        "Personal Library Formatting Standard (Stage 9)\n\n"
        "UNIVERSAL RULES:\n"
        "1. One-screen readability\n"
        "2. Keep writing short (2-4 bullets, max 3 lines per paragraph)\n"
        "3. Consistent field order everywhere\n"
        "4. Prefer relations over copy-paste\n"
        "5. Use fixed status vocabulary\n"
        "6. Every entry has date + tag\n"
        "7. Archive instead of delete\n\n"
        "9-FIELD ORDER (all types):\n"
        "1. Title\n"
        "2. Type/Category\n"
        "3. Status\n"
        "4. Priority/Confidence\n"
        "5. Summary/Definition\n"
        "6. Key Points\n"
        "7. Relations\n"
        "8. Source\n"
        "9. Date Added/Updated\n\n"
        "NAMING STANDARD:\n"
        "Titles: Title Case\n"
        "Tags: lowercase-hyphen format (#deep-dive, #decision-making)\n"
        "Max 5 tags per entry\n\n"
        "MAINTENANCE:\n"
        "Weekly (15 min): Fix missing Status, merge duplicate tags, archive old drafts\n"
        "Monthly (30 min): Review stale entries, promote good drafts, consolidate tags\n"
        "Quarterly (1 hour): Publish ready items, reassess priorities, reflect\n\n"
        "See docs/personal-library-formatting-guide.md for full details."
    )

    try:
        path = _capture_entry("reference", guide_title, guide_body, status="active")
        logger.info("Formatting guide saved to local library: %s", path)
        return f"✅ Formatting guide saved to local library.\n{path}"
    except Exception as e:
        logger.error("Failed to save formatting guide: %s", e)
        return f"❌ Failed to save formatting guide: {str(e)}"
