#!/usr/bin/env python3
"""Diagnose library Firestore integration — list entries, test queries, compare with filesystem."""

from __future__ import annotations

import json
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


def main() -> int:
    print("=" * 60)
    print("LIBRARY FIRESTORE DIAGNOSTIC")
    print("=" * 60)

    # 1. Check config
    print("\n📋 1. CONFIG CHECK")
    from src.core.config import USE_FIRESTORE_LIBRARY, FIREBASE_CREDENTIALS_PATH
    print(f"   USE_FIRESTORE_LIBRARY = {USE_FIRESTORE_LIBRARY}")
    print(f"   FIREBASE_CREDENTIALS_PATH = {FIREBASE_CREDENTIALS_PATH}")
    print(f"   FIREBASE_CREDENTIALS_PATH exists = {Path(FIREBASE_CREDENTIALS_PATH).exists() if FIREBASE_CREDENTIALS_PATH else False}")

    # 2. Count filesystem entries
    print("\n📁 2. FILESYSTEM ENTRIES")
    library_root = _PROJECT_ROOT / "library"
    section_dirs = {
        "profile": "profile",
        "term": "terms",
        "book": "books",
        "article": "articles",
        "thought": "thoughts",
        "reference": "references",
        "research": "research",
    }
    total_fs = 0
    for section, dirname in section_dirs.items():
        dir_path = library_root / dirname
        if dir_path.exists():
            count = sum(1 for _ in dir_path.rglob("*.md"))
            total_fs += count
            print(f"   {section}: {count} files in library/{dirname}/")
    print(f"   TOTAL filesystem: {total_fs}")

    # 3. Count Firestore entries
    print("\n🔥 3. FIRESTORE ENTRIES")
    try:
        from src.integrations.firebase.firestore import _client, _COLLECTION
        from google.cloud.firestore import Query

        db = _client()
        docs = list(db.collection(_COLLECTION).stream())
        print(f"   Total documents in '{_COLLECTION}': {len(docs)}")

        # Count by section
        sections: dict[str, int] = {}
        statuses: dict[str, int] = {}
        types: dict[str, int] = {}
        for doc in docs:
            data = doc.to_dict()
            if data:
                sections[data.get("section", "unknown")] = sections.get(data.get("section", "unknown"), 0) + 1
                statuses[data.get("status", "unknown")] = statuses.get(data.get("status", "unknown"), 0) + 1
                types[data.get("type", "unknown")] = types.get(data.get("type", "unknown"), 0) + 1

        print(f"\n   By section:")
        for sec, count in sorted(sections.items()):
            print(f"      {sec}: {count}")

        print(f"\n   By status:")
        for st, count in sorted(statuses.items()):
            print(f"      {st}: {count}")

        print(f"\n   By type:")
        for t, count in sorted(types.items()):
            print(f"      {t}: {count}")

        # 4. Test list_library_entries queries
        print("\n🔍 4. TESTING list_library_entries()")
        from src.integrations.firebase.firestore import list_library_entries

        # No filters
        try:
            result = list_library_entries(page=1, per_page=5)
            print(f"   No filters: {len(result['entries'])} entries (total={result['total']})")
            if result['entries']:
                print(f"      First: {result['entries'][0].get('title', 'N/A')} (section={result['entries'][0].get('section')})")
        except Exception as e:
            print(f"   No filters: FAILED - {e}")

        # Filter by section=article
        try:
            result = list_library_entries(section="article", page=1, per_page=5)
            print(f"   section=article: {len(result['entries'])} entries (total={result['total']})")
        except Exception as e:
            print(f"   section=article: FAILED - {e}")
            print(f"      ^ This likely means you need a Firestore composite index!")

        # Filter by section=articles (wrong name)
        try:
            result = list_library_entries(section="articles", page=1, per_page=5)
            print(f"   section=articles: {len(result['entries'])} entries (total={result['total']})")
        except Exception as e:
            print(f"   section=articles: FAILED - {e}")

        # 5. Test search
        print("\n🔍 5. TESTING search_library_entries()")
        from src.integrations.firebase.firestore import search_library_entries

        try:
            result = search_library_entries("", limit=5)
            print(f"   Empty query: {len(result)} entries")
        except Exception as e:
            print(f"   Empty query: FAILED - {e}")

        # 6. Test store abstraction
        print("\n📦 6. TESTING _get_store()")
        from src.core.libraries import _get_store
        store = _get_store()
        print(f"   Store type: {type(store).__name__}")

        try:
            result = store.list_entries(page=1, per_page=5)
            print(f"   store.list_entries(): {len(result['entries'])} entries (total={result['total']})")
        except Exception as e:
            print(f"   store.list_entries(): FAILED - {e}")

        try:
            sections_list = store.list_sections()
            print(f"   store.list_sections(): {sections_list}")
        except Exception as e:
            print(f"   store.list_sections(): FAILED - {e}")

        # 7. Check specific article entries
        print("\n📄 7. SAMPLE ARTICLE ENTRIES")
        article_docs = [d for d in docs if d.to_dict().get("section") == "article"]
        for doc in article_docs[:3]:
            data = doc.to_dict()
            print(f"   - {doc.id}: title='{data.get('title', 'N/A')[:50]}' status={data.get('status')} type={data.get('type')}")

    except Exception as e:
        print(f"\n❌ Firestore connection failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
