"""Library storage abstraction: filesystem or Firestore.

Current implementation stores captures as markdown files under library/.
This keeps Stage 9 local-first and file-based for predictable versioning.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import re
from typing import Any, Optional


class _LibraryStore(ABC):
    """Abstract base for library storage backends."""

    # --- Write operations ---
    @abstractmethod
    def save_entry(
        self,
        section: str,
        title: str,
        body: str,
        *,
        status: str = "draft",
        tags: list[str] | None = None,
        source_url: Optional[str] = None,
    ) -> str:
        """Persist a single library entry. Returns relative path."""

    @abstractmethod
    def update_entry(self, entry_id: str, updates: dict[str, Any]) -> bool:
        """Update an existing entry by entry_id. Returns True if found."""

    @abstractmethod
    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry. Returns True if found."""

    # --- Read operations ---
    @abstractmethod
    def get_entry(self, entry_id: str) -> Optional[dict[str, Any]]:
        """Get full entry including markdown content."""

    @abstractmethod
    def search_entries(
        self,
        query: str,
        section: Optional[str] = None,
        limit: int = 12,
    ) -> list[dict[str, Any]]:
        """Search entries by query text."""

    @abstractmethod
    def search_all_entries(self, query: str, limit: int = 12) -> list[str]:
        """Full-text search across all markdown files. Returns paths."""

    @abstractmethod
    def list_entries(
        self,
        section: Optional[str] = None,
        status: Optional[str] = None,
        tag: Optional[str] = None,
        source_url: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:
        """Paginated list of entries with metadata only."""

    @abstractmethod
    def list_sections(self) -> list[str]:
        """Return all distinct sections."""

    @abstractmethod
    def list_tags(self) -> list[str]:
        """Return all distinct tags."""

    @abstractmethod
    def build_index(self) -> dict[str, Any]:
        """Build and return the full library index."""

    @abstractmethod
    def load_index(self) -> dict[str, Any]:
        """Load or build the library index."""

    @abstractmethod
    def count_entries(self, section: str) -> int:
        """Count entries in a section."""

    @abstractmethod
    def recent_entries(self, section: str, limit: int = 10) -> list[str]:
        """Return recent entry paths for a section, newest first."""

    @abstractmethod
    def find_bundles(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search bundle indexes."""

    @abstractmethod
    def get_bundle_summary(self, bundle_path: str) -> str:
        """Extract summary from a bundle index."""


class _FileLibraryStore(_LibraryStore):
    """Filesystem-only library store. Current behavior, extracted."""

    def __init__(
        self,
        project_root: Path,
        library_root: Path,
        index_path: Path,
    ) -> None:
        self._project_root = project_root
        self._library_root = library_root
        self._index_path = index_path
        self._section_dirs = {
            "profile": "profile",
            "term": "terms",
            "book": "books",
            "article": "articles",
            "thought": "thoughts",
            "reference": "references",
            "research": "research",
        }

    # --- Internal helpers ---

    def _ensure_library_dirs(self) -> None:
        self._library_root.mkdir(parents=True, exist_ok=True)
        for dirname in self._section_dirs.values():
            (self._library_root / dirname).mkdir(parents=True, exist_ok=True)

    def _resolve_section_dir(self, section: str) -> str:
        known = self._section_dirs.get(section)
        if known:
            return known
        return self._slugify(section)

    @staticmethod
    def _slugify(text: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
        return slug[:80] or "entry"

    @staticmethod
    def _match_index_records(
        records: list[dict[str, Any]], query: str, limit: int = 8
    ) -> list[dict[str, Any]]:
        q = query.lower().strip()
        results = []
        for record in records:
            haystacks = [
                str(record.get("title", "")).lower(),
                str(record.get("path", "")).lower(),
                str(record.get("section", "")).lower(),
                str(record.get("category", "")).lower(),
            ]
            if any(q in value for value in haystacks):
                results.append(record)
                if len(results) >= limit:
                    break
        return results

    # --- Write operations ---

    def save_entry(
        self,
        section: str,
        title: str,
        body: str,
        *,
        status: str = "draft",
        tags: list[str] | None = None,
        source_url: Optional[str] = None,
    ) -> str:
        self._ensure_library_dirs()
        dirname = self._resolve_section_dir(section)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        slug = self._slugify(title)
        path = self._library_root / dirname / f"{ts}-{slug}.md"
        metadata_tags = ", ".join(tags or [])
        source_url_line = f"source_url: {source_url}\n" if source_url else ""
        content = (
            f"---\n"
            f"title: {title}\n"
            f"section: {section}\n"
            f"status: {status}\n"
            f"tags: [{metadata_tags}]\n"
            f"captured_at: {datetime.now().isoformat(timespec='minutes')}\n"
            f"{source_url_line}"
            f"---\n\n"
            f"{body}\n"
        )
        path.write_text(content, encoding="utf-8")
        self.build_index()
        return str(path.relative_to(self._project_root))

    def save_bundle_index(
        self,
        bundle_dir: Path,
        title: str,
        category: str,
        section_dir: str,
        item_type: str,
        tags: list[str],
        source_url: Optional[str],
        research_mode: str,
    ) -> None:
        """Write a bundle index.md file."""
        source_url_line = f"source_url: {source_url}\n" if source_url else ""
        metadata = (
            f"---\n"
            f"title: {title}\n"
            f"category: {category}\n"
            f"storage_folder: {section_dir}\n"
            f"item_type: {item_type}\n"
            f"tags: [{', '.join(tags)}]\n"
            f"captured_at: {datetime.now().isoformat(timespec='minutes')}\n"
            f"research_mode: {research_mode}\n"
            f"{source_url_line}"
            f"---\n\n"
        )
        (bundle_dir / "index.md").write_text(metadata, encoding="utf-8")

    def update_entry(self, entry_id: str, updates: dict[str, Any]) -> bool:
        """Update an entry by ID. Currently not used directly — handled in api/library.py."""
        return False

    def delete_entry(self, entry_id: str) -> bool:
        return False

    # --- Read operations ---

    def get_entry(self, entry_id: str) -> Optional[dict[str, Any]]:
        """Get full entry with markdown content."""
        index = self.load_index()
        for record in index.get("entries", []):
            path = record.get("path", "")
            # Derive ID from path
            rec_id = self._entry_id_from_path(path)
            if rec_id == entry_id:
                full_path = self._project_root / path
                if full_path.exists():
                    text = full_path.read_text(encoding="utf-8", errors="ignore")
                    record["markdown"] = text
                    return record
        return None

    @staticmethod
    def _entry_id_from_path(path: str) -> str:
        """Derive entry ID from path."""
        parts = path.split("/")
        filename = parts[-1]
        if filename == "index.md":
            # Bundle: use parent directory name
            return parts[-2] if len(parts) > 1 else filename
        return Path(filename).stem

    def search_entries(
        self,
        query: str,
        section: Optional[str] = None,
        limit: int = 12,
    ) -> list[dict[str, Any]]:
        index = self.load_index()
        records = index.get("entries", [])
        if section:
            records = [r for r in records if r.get("section") == section]
        return self._match_index_records(records, query, limit=limit)

    def search_all_entries(self, query: str, limit: int = 12) -> list[str]:
        self._ensure_library_dirs()
        q = query.lower().strip()
        matches: list[Path] = []
        for path in sorted(self._library_root.rglob("*.md"), reverse=True):
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            if q in text:
                matches.append(path)
                if len(matches) >= limit:
                    break
        return [str(p.relative_to(self._project_root)) for p in matches]

    def list_entries(
        self,
        section: Optional[str] = None,
        status: Optional[str] = None,
        tag: Optional[str] = None,
        source_url: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:
        index = self.load_index()
        entries = index.get("entries", [])

        if section:
            entries = [e for e in entries if e.get("section") == section]
        if status:
            entries = [e for e in entries if e.get("status") == status]
        if tag:
            entries = [e for e in entries if tag in e.get("tags", [])]
        if source_url:
            entries = [e for e in entries if e.get("source_url") == source_url]

        total = len(entries)
        start = (page - 1) * per_page
        page_entries = entries[start : start + per_page]

        return {
            "entries": page_entries,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    def list_sections(self) -> list[str]:
        return sorted(self._section_dirs.keys())

    def list_tags(self) -> list[str]:
        index = self.load_index()
        tags: set[str] = set()
        for entry in index.get("entries", []):
            tags.update(entry.get("tags", []))
        return sorted(tags)

    def build_index(self) -> dict[str, Any]:
        self._ensure_library_dirs()
        entries: list[dict[str, Any]] = []
        bundles: list[dict[str, Any]] = []

        for path in sorted(self._library_root.rglob("*.md")):
            if path == self._index_path:
                continue
            rel_path = str(path.relative_to(self._project_root))
            if any(part.startswith(".") for part in path.parts):
                continue
            if path.parent != self._library_root / path.parent.name and path.name != "index.md":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            title_match = re.search(r"^title:\s*(.+)$", text, flags=re.MULTILINE)
            section_match = re.search(r"^section:\s*(.+)$", text, flags=re.MULTILINE)
            category_match = re.search(r"^category:\s*(.+)$", text, flags=re.MULTILINE)
            status_match = re.search(r"^status:\s*(.+)$", text, flags=re.MULTILINE)
            title = title_match.group(1).strip() if title_match else path.stem
            section = section_match.group(1).strip() if section_match else path.parent.name
            category = category_match.group(1).strip() if category_match else section
            status = status_match.group(1).strip() if status_match else "unknown"
            source_url_match = re.search(r"^source_url:\s*(.+)$", text, flags=re.MULTILINE)
            source_url = source_url_match.group(1).strip() if source_url_match else None
            tags_match = re.search(r"^tags:\s*(.+)$", text, flags=re.MULTILINE)
            tags_str = tags_match.group(1).strip() if tags_match else ""
            tags = [t.strip() for t in tags_str.strip("[]").split(",") if t.strip()]
            record = {
                "title": title,
                "path": rel_path,
                "section": section,
                "category": category,
                "status": status,
                "type": "bundle-index" if path.name == "index.md" and path.parent != (self._library_root / self._resolve_section_dir(section)) else "entry",
                "source_url": source_url,
                "tags": tags,
                "updated_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="minutes"),
            }
            entries.append(record)

        for path in sorted(self._library_root.rglob("index.md")):
            if path.parent == self._library_root:
                continue
            rel_path = str(path.parent.relative_to(self._project_root))
            text = path.read_text(encoding="utf-8", errors="ignore")
            title_match = re.search(r"^title:\s*(.+)$", text, flags=re.MULTILINE)
            category_match = re.search(r"^category:\s*(.+)$", text, flags=re.MULTILINE)
            title = title_match.group(1).strip() if title_match else path.parent.name
            category = category_match.group(1).strip() if category_match else path.parent.parent.name
            bundles.append(
                {
                    "title": title,
                    "path": rel_path,
                    "category": category,
                    "updated_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="minutes"),
                }
            )

        index = {
            "generated_at": datetime.now().isoformat(timespec="minutes"),
            "entries": entries,
            "bundles": bundles,
        }
        self._index_path.write_text(
            __import__("json").dumps(index, indent=2), encoding="utf-8"
        )
        return index

    def load_index(self) -> dict[str, Any]:
        return self.build_index()

    def count_entries(self, section: str) -> int:
        self._ensure_library_dirs()
        dirname = self._resolve_section_dir(section)
        return sum(1 for _ in (self._library_root / dirname).glob("*.md"))

    def recent_entries(self, section: str, limit: int = 10) -> list[str]:
        self._ensure_library_dirs()
        dirname = self._resolve_section_dir(section)
        paths = sorted(
            (self._library_root / dirname).rglob("*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return [str(p.relative_to(self._project_root)) for p in paths[:limit]]

    def find_bundles(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        index = self.load_index()
        return self._match_index_records(index.get("bundles", []), query, limit=limit)

    def get_bundle_summary(self, bundle_path: str) -> str:
        index_file = self._project_root / bundle_path / "index.md"
        if not index_file.exists():
            return "Bundle index not found."
        text = index_file.read_text(encoding="utf-8", errors="ignore")
        summary_match = re.search(r"## Summary\n\n(.+?)(\n## |$)", text, flags=re.DOTALL)
        track_match = re.search(r"## Information To Track\n\n(.+?)(\n## |$)", text, flags=re.DOTALL)
        parts = []
        if summary_match:
            parts.append("Summary:\n" + summary_match.group(1).strip())
        if track_match:
            lines = [line.strip() for line in track_match.group(1).splitlines() if line.strip()]
            parts.append("Track:\n" + "\n".join(lines[:5]))
        return "\n\n".join(parts) if parts else "Bundle summary not available."


class _FirestoreLibraryStore(_LibraryStore):
    """Firestore-backed library store with dual-write to filesystem.

    Every write goes to the filesystem first (backup/git history),
    then best-effort to Firestore. If Firestore fails, the operation
    still succeeds — the failure is logged as a warning.

    Reads come from Firestore for speed and queryability.
    """

    def __init__(
        self,
        project_root: Path,
        library_root: Path,
        index_path: Path,
    ) -> None:
        self._file_store = _FileLibraryStore(project_root, library_root, index_path)
        self._project_root = project_root

    def _save_to_firestore(
        self,
        entry_id: str,
        title: str,
        section: str,
        status: str,
        path: str,
        markdown: str,
        tags: list[str] | None = None,
        source_url: Optional[str] = None,
    ) -> None:
        """Best-effort Firestore write. Never raises."""
        import logging

        logger = logging.getLogger(__name__)
        try:
            from src.integrations.firebase.firestore import save_library_entry

            save_library_entry(
                entry_id=entry_id,
                title=title,
                section=section,
                category=section,
                status=status,
                entry_type="entry",
                tags=tags or [],
                source_url=source_url,
                path=path,
                markdown=markdown,
                frontmatter={
                    "title": title,
                    "section": section,
                    "status": status,
                    "tags": tags or [],
                    "source_url": source_url,
                },
            )
        except Exception:
            logger.warning("Firestore library write failed", exc_info=True)

    # --- Write operations ---

    def save_entry(
        self,
        section: str,
        title: str,
        body: str,
        *,
        status: str = "draft",
        tags: list[str] | None = None,
        source_url: Optional[str] = None,
    ) -> str:
        # 1. Always write to filesystem first (backup/git history)
        result = self._file_store.save_entry(
            section=section,
            title=title,
            body=body,
            status=status,
            tags=tags,
            source_url=source_url,
        )

        # 2. Best-effort Firestore write with FULL markdown (frontmatter + body)
        entry_id = Path(result).stem
        full_path = self._project_root / result
        full_markdown = (
            full_path.read_text(encoding="utf-8")
            if full_path.exists()
            else body
        )
        self._save_to_firestore(
            entry_id=entry_id,
            title=title,
            section=section,
            status=status,
            path=result,
            markdown=full_markdown,
            tags=tags,
            source_url=source_url,
        )
        return result

    def save_bundle_index(
        self,
        bundle_dir: Path,
        title: str,
        category: str,
        section_dir: str,
        item_type: str,
        tags: list[str],
        source_url: Optional[str],
        research_mode: str,
    ) -> None:
        self._file_store.save_bundle_index(
            bundle_dir=bundle_dir,
            title=title,
            category=category,
            section_dir=section_dir,
            item_type=item_type,
            tags=tags,
            source_url=source_url,
            research_mode=research_mode,
        )

    def update_entry(self, entry_id: str, updates: dict[str, Any]) -> bool:
        import logging

        logger = logging.getLogger(__name__)
        # Update filesystem
        result = self._file_store.update_entry(entry_id, updates)

        # Best-effort Firestore update
        try:
            from src.integrations.firebase.firestore import update_library_entry

            update_library_entry(entry_id, updates)
        except Exception:
            logger.warning("Firestore library update failed", exc_info=True)

        return result

    def delete_entry(self, entry_id: str) -> bool:
        import logging

        logger = logging.getLogger(__name__)
        # Delete from filesystem
        result = self._file_store.delete_entry(entry_id)

        # Best-effort Firestore delete
        try:
            from src.integrations.firebase.firestore import delete_library_entry

            delete_library_entry(entry_id)
        except Exception:
            logger.warning("Firestore library delete failed", exc_info=True)

        return result

    # --- Read operations ---

    def get_entry(self, entry_id: str) -> Optional[dict[str, Any]]:
        import logging

        logger = logging.getLogger(__name__)
        try:
            from src.integrations.firebase.firestore import get_library_entry

            data = get_library_entry(entry_id)
            if data:
                return data
        except Exception:
            logger.warning("Firestore library read failed, falling back to filesystem", exc_info=True)

        return self._file_store.get_entry(entry_id)

    def search_entries(
        self,
        query: str,
        section: Optional[str] = None,
        limit: int = 12,
    ) -> list[dict[str, Any]]:
        import logging

        logger = logging.getLogger(__name__)
        try:
            from src.integrations.firebase.firestore import search_library_entries

            return search_library_entries(
                query=query,
                section=section,
                limit=limit,
            )
        except Exception:
            logger.warning("Firestore library search failed, falling back to filesystem", exc_info=True)

        return self._file_store.search_entries(query, section=section, limit=limit)

    def search_all_entries(self, query: str, limit: int = 12) -> list[str]:
        return self._file_store.search_all_entries(query, limit)

    def list_entries(
        self,
        section: Optional[str] = None,
        status: Optional[str] = None,
        tag: Optional[str] = None,
        source_url: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:
        import logging

        logger = logging.getLogger(__name__)
        try:
            from src.integrations.firebase.firestore import list_library_entries

            return list_library_entries(
                section=section,
                status=status,
                tag=tag,
                source_url=source_url,
                page=page,
                per_page=per_page,
            )
        except Exception:
            logger.warning("Firestore library list failed, falling back to filesystem", exc_info=True)

        return self._file_store.list_entries(
            section=section,
            status=status,
            tag=tag,
            source_url=source_url,
            page=page,
            per_page=per_page,
        )

    def list_sections(self) -> list[str]:
        import logging

        logger = logging.getLogger(__name__)
        try:
            from src.integrations.firebase.firestore import list_library_sections

            return list_library_sections()
        except Exception:
            logger.warning("Firestore list_sections failed, falling back to filesystem", exc_info=True)

        return self._file_store.list_sections()

    def list_tags(self) -> list[str]:
        import logging

        logger = logging.getLogger(__name__)
        try:
            from src.integrations.firebase.firestore import list_library_tags

            return list_library_tags()
        except Exception:
            logger.warning("Firestore list_tags failed, falling back to filesystem", exc_info=True)

        return self._file_store.list_tags()

    def build_index(self) -> dict[str, Any]:
        import logging

        logger = logging.getLogger(__name__)
        try:
            from src.integrations.firebase.firestore import get_library_index

            return get_library_index()
        except Exception:
            logger.warning("Firestore index failed, falling back to filesystem", exc_info=True)

        return self._file_store.build_index()

    def load_index(self) -> dict[str, Any]:
        return self.build_index()

    def count_entries(self, section: str) -> int:
        import logging

        logger = logging.getLogger(__name__)
        try:
            from src.integrations.firebase.firestore import count_library_entries

            return count_library_entries(section)
        except Exception:
            logger.warning("Firestore count failed, falling back to filesystem", exc_info=True)

        return self._file_store.count_entries(section)

    def recent_entries(self, section: str, limit: int = 10) -> list[str]:
        return self._file_store.recent_entries(section, limit)

    def find_bundles(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        import logging

        logger = logging.getLogger(__name__)
        try:
            from src.integrations.firebase.firestore import search_library_entries

            results = search_library_entries(query=query, limit=limit)
            return [r for r in results if r.get("type") == "bundle-index"]
        except Exception:
            logger.warning("Firestore bundle search failed, falling back to filesystem", exc_info=True)

        return self._file_store.find_bundles(query, limit)

    def get_bundle_summary(self, bundle_path: str) -> str:
        return self._file_store.get_bundle_summary(bundle_path)
