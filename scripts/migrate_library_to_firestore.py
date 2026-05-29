#!/usr/bin/env python3
"""Migrate existing library markdown files to Firestore.

Usage:
    # Dry run (show what would be migrated)
    python scripts/migrate_library_to_firestore.py --dry-run

    # Actual migration
    python scripts/migrate_library_to_firestore.py

    # Migrate specific sections only
    python scripts/migrate_library_to_firestore.py --sections articles,books,terms

Environment:
    Requires FIREBASE_CREDENTIALS_PATH or FIREBASE_CREDENTIALS_JSON to be set.
    Set USE_FIRESTORE_LIBRARY=true in .env for the brain to read from Firestore.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

# Auto-detect and use project venv if available
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_VENV_PYTHON = _PROJECT_ROOT / ".venv" / "bin" / "python3"
if _VENV_PYTHON.exists() and sys.executable != str(_VENV_PYTHON):
    import os
    os.execv(str(_VENV_PYTHON), [str(_VENV_PYTHON), __file__] + sys.argv[1:])

# Add project root to path
sys.path.insert(0, str(_PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_frontmatter(text: str) -> dict:
    """Extract frontmatter fields from markdown text."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}
    front = parts[1]
    result: dict[str, str | list[str] | None] = {}
    for line in front.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if key == "tags":
                if val.startswith("["):
                    try:
                        result[key] = json.loads(val.replace("'", '"'))
                    except Exception:
                        result[key] = [t.strip() for t in val.strip("[]").split(",") if t.strip()]
                else:
                    result[key] = [t.strip() for t in val.strip("[]").split(",") if t.strip()]
            elif key in ("source_url", "captured_at", "title", "section", "status", "category", "research_mode", "item_type", "storage_folder"):
                result[key] = val or None
    return result


def find_library_files(project_root: Path, sections: list[str] | None = None) -> list[Path]:
    """Find all markdown files in the library directory."""
    library_root = project_root / "library"
    if not library_root.exists():
        logger.error("Library directory not found: %s", library_root)
        return []

    files: list[Path] = []
    section_dirs = {
        "profile": "profile",
        "term": "terms",
        "book": "books",
        "article": "articles",
        "thought": "thoughts",
        "reference": "references",
        "research": "research",
    }

    for section, dirname in section_dirs.items():
        if sections and section not in sections:
            continue
        dir_path = library_root / dirname
        if not dir_path.exists():
            continue
        for path in sorted(dir_path.rglob("*.md")):
            if path.name == "index.json":
                continue
            files.append(path)

    return files


def migrate_file(
    path: Path,
    project_root: Path,
    dry_run: bool,
    force: bool,
    stats: dict[str, int],
) -> bool:
    """Migrate a single markdown file to Firestore. Returns True if migrated."""
    rel_path = str(path.relative_to(project_root))
    entry_id = path.stem

    text = path.read_text(encoding="utf-8", errors="ignore")
    fm = parse_frontmatter(text)

    section = str(fm.get("section", path.parent.name))
    title = str(fm.get("title", path.stem))
    category = str(fm.get("category", section))
    status = str(fm.get("status", "draft"))
    tags = fm.get("tags", [])
    source_url = fm.get("source_url")

    # Determine entry type
    is_bundle_index = path.name == "index.md" and path.parent != (project_root / "library" / section)
    entry_type = "bundle-index" if is_bundle_index else "entry"

    if dry_run:
        logger.info(
            "[DRY RUN] Would migrate: %s | section=%s | title=%s | type=%s | size=%d bytes",
            rel_path, section, title[:50], entry_type, len(text),
        )
        stats["dry_run"] += 1
        return True

    # Check if entry already exists in Firestore
    if not force:
        try:
            from src.integrations.firebase.firestore import _client, _COLLECTION
            existing = _client().collection(_COLLECTION).document(entry_id).get()
            if existing.exists:
                logger.debug("Skipping (already exists): %s", entry_id)
                stats["skipped"] += 1
                return False
        except Exception as exc:
            logger.warning("Could not check existing entry %s: %s", entry_id, exc)

    try:
        from src.integrations.firebase.firestore import save_library_entry

        save_library_entry(
            entry_id=entry_id,
            title=title,
            section=section,
            category=category,
            status=status,
            entry_type=entry_type,
            tags=tags if isinstance(tags, list) else [],
            source_url=source_url,
            path=rel_path,
            markdown=text,
            frontmatter={k: v for k, v in fm.items() if v is not None},
        )
        logger.info("Migrated: %s | %s", entry_id, title[:50])
        stats["migrated"] += 1
        return True
    except Exception as exc:
        logger.error("Failed to migrate %s: %s", entry_id, exc)
        stats["failed"] += 1
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate library markdown files to Firestore")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without uploading")
    parser.add_argument("--sections", type=str, help="Comma-separated list of sections to migrate (default: all)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing Firestore entries")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    project_root = Path(__file__).resolve().parents[1]

    sections: list[str] | None = None
    if args.sections:
        sections = [s.strip() for s in args.sections.split(",")]

    files = find_library_files(project_root, sections)
    logger.info("Found %d markdown files to process", len(files))

    if not files:
        logger.warning("No files found. Nothing to migrate.")
        return 0

    stats: dict[str, int] = {"migrated": 0, "skipped": 0, "failed": 0, "dry_run": 0}

    for path in files:
        migrate_file(path, project_root, args.dry_run, args.force, stats)

    # Summary
    if args.dry_run:
        logger.info("=" * 50)
        logger.info("DRY RUN COMPLETE")
        logger.info("Would migrate: %d files", stats["dry_run"])
        logger.info("Run without --dry-run to perform the migration.")
    else:
        logger.info("=" * 50)
        logger.info("MIGRATION COMPLETE")
        logger.info("Migrated: %d | Skipped: %d | Failed: %d", stats["migrated"], stats["skipped"], stats["failed"])

        if stats["migrated"] > 0:
            logger.info("")
            logger.info("Next steps:")
            logger.info("  1. Set USE_FIRESTORE_LIBRARY=true in your .env file")
            logger.info("  2. Restart the brain API")
            logger.info("  3. Dashboard reads will now come from Firestore")

    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
