#!/usr/bin/env python3
"""Clean up incorrectly migrated bundle sub-files from Firestore library_entries.

Bundle sub-files (like 01-raw-input.md, 02-search-history.md) inside research/
 bundles were incorrectly migrated as standalone entries. They should only exist
 as part of their bundle, not as separate indexed entries.

Usage:
    python scripts/cleanup_firestore_library.py --dry-run   # Preview
    python scripts/cleanup_firestore_library.py             # Execute cleanup
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Auto-detect venv
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_VENV_PYTHON = _PROJECT_ROOT / ".venv" / "bin" / "python3"
if _VENV_PYTHON.exists() and sys.executable != str(_VENV_PYTHON):
    import os
    os.execv(str(_VENV_PYTHON), [str(_VENV_PYTHON), __file__] + sys.argv[1:])

sys.path.insert(0, str(_PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

_LIBRARY_ROOT = _PROJECT_ROOT / "library"
_COLLECTION = "library_entries"
_CHUNK_COLLECTION = "chunks"


def _should_include_file(path: Path, library_root: Path) -> bool:
    """Mirror _FileLibraryStore.build_index() logic."""
    if path.name == "index.json":
        return False
    if any(part.startswith(".") for part in path.parts):
        return False
    if path.parent != library_root / path.parent.name and path.name != "index.md":
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean up invalid Firestore library entries")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be deleted")
    args = parser.parse_args()

    print("=" * 60)
    print("FIRESTORE LIBRARY CLEANUP")
    print("=" * 60)

    try:
        from src.integrations.firebase.firestore import _client, _COLLECTION
    except Exception as exc:
        logger.error("Failed to connect to Firestore: %s", exc)
        return 1

    db = _client()
    docs = list(db.collection(_COLLECTION).stream())

    to_delete: list[tuple[str, str, str]] = []  # (doc_id, path, reason)
    valid: list[tuple[str, str]] = []

    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue

        path_str = data.get("path", "")
        entry_id = doc.id
        section = data.get("section", "")

        # Check 1: path points to a bundle sub-file
        if path_str:
            rel_path = _PROJECT_ROOT / path_str
            # Check if this path would pass the include filter
            if not _should_include_file(rel_path, _LIBRARY_ROOT):
                to_delete.append((entry_id, path_str, "bundle sub-file (not index.md in subdir)"))
                continue

        # Check 2: section name looks like a bundle directory (contains timestamps)
        if section and len(section) > 30 and any(c.isdigit() for c in section):
            to_delete.append((entry_id, path_str, f"invalid section name: {section[:50]}"))
            continue

        valid.append((entry_id, path_str))

    print(f"\n📊 SCAN RESULTS")
    print(f"   Total Firestore docs: {len(docs)}")
    print(f"   Valid entries: {len(valid)}")
    print(f"   Invalid entries to remove: {len(to_delete)}")

    if to_delete:
        print(f"\n🗑️  ENTRIES TO DELETE:")
        for entry_id, path_str, reason in to_delete:
            print(f"   • {entry_id}")
            print(f"     path: {path_str}")
            print(f"     reason: {reason}")

        if args.dry_run:
            print(f"\n[DRY RUN] No changes made. Run without --dry-run to execute cleanup.")
        else:
            print(f"\n🧹 DELETING...")
            deleted = 0
            for entry_id, path_str, reason in to_delete:
                try:
                    # Delete chunks first
                    chunks = (
                        db.collection(_COLLECTION)
                        .document(entry_id)
                        .collection(_CHUNK_COLLECTION)
                        .stream()
                    )
                    for chunk in chunks:
                        chunk.reference.delete()

                    # Delete main doc
                    db.collection(_COLLECTION).document(entry_id).delete()
                    deleted += 1
                    logger.info("Deleted %s (%s)", entry_id, reason)
                except Exception as exc:
                    logger.error("Failed to delete %s: %s", entry_id, exc)

            print(f"\n✅ Cleanup complete. Deleted {deleted}/{len(to_delete)} invalid entries.")

    print(f"\n✅ VALID ENTRIES REMAINING: {len(valid)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
