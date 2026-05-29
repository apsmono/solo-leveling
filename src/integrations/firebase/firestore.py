"""Firestore client wrappers for reminders, command logging, and library entries."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from src.integrations.firebase.auth import _init_firebase

logger = logging.getLogger(__name__)

_firestore_client: Any | None = None


def _client() -> Any:
    global _firestore_client
    if _firestore_client is None:
        _init_firebase()
        from google.cloud import firestore
        _firestore_client = firestore.client()
    return _firestore_client


# ---------------------------------------------------------------------------
# Reminders
# ---------------------------------------------------------------------------

def create_reminder_doc(message: str, run_at: datetime, source: str = "api") -> str:
    doc_ref = _client().collection("reminders").document()
    doc_ref.set({
        "message": message,
        "run_at": run_at,
        "created_at": datetime.now(),
        "sent_at": None,
        "source": source,
    })
    return doc_ref.id


def list_pending_reminders() -> list[dict[str, Any]]:
    docs = (
        _client()
        .collection("reminders")
        .where("sent_at", "==", None)
        .order_by("run_at")
        .stream()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


def mark_reminder_sent(doc_id: str) -> None:
    _client().collection("reminders").document(doc_id).update({"sent_at": datetime.now()})


def delete_reminder_doc(doc_id: str) -> None:
    """Delete a reminder document by id (dashboard / API cancel)."""
    _client().collection("reminders").document(doc_id).delete()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def log_command(text: str, intent: str, reply: str, source: str = "api") -> None:
    _client().collection("commands").add({
        "text": text,
        "intent": intent,
        "reply": reply,
        "source": source,
        "created_at": datetime.now(),
    })


def list_recent_commands(limit: int = 50) -> list[dict[str, Any]]:
    from google.cloud.firestore import Query
    docs = (
        _client()
        .collection("commands")
        .order_by("created_at", direction=Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


# ---------------------------------------------------------------------------
# Library
# ---------------------------------------------------------------------------

_COLLECTION = "library_entries"
_CHUNK_COLLECTION = "chunks"
_INDEX_DOC = "library_index"


def save_library_entry(
    entry_id: str,
    title: str,
    section: str,
    category: str,
    status: str,
    entry_type: str,
    tags: list[str],
    source_url: str | None,
    path: str,
    markdown: str,
    frontmatter: dict[str, Any],
) -> None:
    """Save a library entry to Firestore with compression and chunking."""
    from src.core.library_compression import compress_content, chunk_content

    stored_content, is_compressed, needs_chunking = compress_content(markdown)

    doc_ref = _client().collection(_COLLECTION).document(entry_id)

    base_doc: dict[str, Any] = {
        "entry_id": entry_id,
        "title": title,
        "section": section,
        "category": category,
        "status": status,
        "type": entry_type,
        "tags": tags,
        "source_url": source_url,
        "captured_at": datetime.now(),
        "updated_at": datetime.now(),
        "path": path,
        "compressed": is_compressed,
        "chunked": needs_chunking,
        "frontmatter": frontmatter,
        "search_text": f"{title} {section} {category} {' '.join(tags)} {markdown[:5000]}".lower(),
    }

    if needs_chunking:
        base_doc["markdown"] = None
        doc_ref.set(base_doc)

        # Delete old chunks first
        _delete_chunks(entry_id)

        # Write new chunks
        chunks = chunk_content(markdown)
        for idx, chunk in enumerate(chunks):
            doc_ref.collection(_CHUNK_COLLECTION).document(str(idx)).set({
                "chunk_index": idx,
                "content": chunk,
                "total_chunks": len(chunks),
            })
    else:
        base_doc["markdown"] = stored_content
        doc_ref.set(base_doc)

    logger.info("Saved library entry %s to Firestore (chunked=%s)", entry_id, needs_chunking)


def get_library_entry(entry_id: str) -> dict[str, Any] | None:
    """Get full entry with decompression and chunk reassembly."""
    from src.core.library_compression import decompress_content, reassemble_chunks

    doc_ref = _client().collection(_COLLECTION).document(entry_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None

    data = doc.to_dict()
    if data is None:
        return None

    if data.get("chunked"):
        chunks = (
            doc_ref.collection(_CHUNK_COLLECTION)
            .order_by("chunk_index")
            .stream()
        )
        chunk_data = [c.to_dict()["content"] for c in chunks if c.to_dict()]
        data["markdown"] = reassemble_chunks(chunk_data)
    elif data.get("compressed"):
        data["markdown"] = decompress_content(data["markdown"], is_compressed=True)

    return data


def _delete_chunks(entry_id: str) -> None:
    """Delete all chunks for an entry."""
    chunks = (
        _client()
        .collection(_COLLECTION)
        .document(entry_id)
        .collection(_CHUNK_COLLECTION)
        .stream()
    )
    for chunk in chunks:
        chunk.reference.delete()


def update_library_entry(entry_id: str, updates: dict[str, Any]) -> bool:
    """Update an existing library entry."""
    doc_ref = _client().collection(_COLLECTION).document(entry_id)
    doc = doc_ref.get()
    if not doc.exists:
        return False

    # If markdown is being updated, re-compress
    if "markdown" in updates:
        from src.core.library_compression import compress_content

        stored_content, is_compressed, needs_chunking = compress_content(updates["markdown"])
        updates["markdown"] = stored_content
        updates["compressed"] = is_compressed
        updates["chunked"] = needs_chunking

        if needs_chunking:
            from src.core.library_compression import chunk_content

            updates["markdown"] = None
            _delete_chunks(entry_id)
            chunks = chunk_content(updates.pop("markdown_original", updates["markdown"]))
            for idx, chunk in enumerate(chunks):
                doc_ref.collection(_CHUNK_COLLECTION).document(str(idx)).set({
                    "chunk_index": idx,
                    "content": chunk,
                    "total_chunks": len(chunks),
                })

    updates["updated_at"] = datetime.now()
    doc_ref.update(updates)
    return True


def delete_library_entry(entry_id: str) -> bool:
    """Delete a library entry and its chunks."""
    doc_ref = _client().collection(_COLLECTION).document(entry_id)
    doc = doc_ref.get()
    if not doc.exists:
        return False

    _delete_chunks(entry_id)
    doc_ref.delete()
    return True


def search_library_entries(
    query: str,
    section: str | None = None,
    status: str | None = None,
    tag: str | None = None,
    source_url: str | None = None,
    limit: int = 12,
) -> list[dict[str, Any]]:
    """Search library entries. Falls back to client-side text search."""
    collection = _client().collection(_COLLECTION)

    # Build query chain
    q = collection
    if section:
        q = q.where("section", "==", section)
    if status:
        q = q.where("status", "==", status)
    if tag:
        q = q.where("tags", "array_contains", tag)
    if source_url:
        q = q.where("source_url", "==", source_url)

    # Over-fetch for client-side filtering
    docs = q.limit(limit * 3).stream()
    results = []
    q_lower = query.lower()

    for doc in docs:
        data = doc.to_dict()
        if data is None:
            continue
        search_text = data.get("search_text", "")
        if q_lower in search_text or q_lower in data.get("title", "").lower():
            # Don't include full markdown in search results (metadata only)
            data.pop("markdown", None)
            data["id"] = doc.id
            results.append(data)
            if len(results) >= limit:
                break

    return results


def list_library_entries(
    section: str | None = None,
    status: str | None = None,
    tag: str | None = None,
    source_url: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """Paginated list of library entries from Firestore."""
    collection = _client().collection(_COLLECTION)
    q = collection

    if section:
        q = q.where("section", "==", section)
    if status:
        q = q.where("status", "==", status)
    if tag:
        q = q.where("tags", "array_contains", tag)
    if source_url:
        q = q.where("source_url", "==", source_url)

    from google.cloud.firestore import Query
    q = q.order_by("updated_at", direction=Query.DESCENDING)

    # Simple pagination: fetch all up to page * per_page, then slice
    # For large libraries, cursor-based pagination would be better
    all_docs = list(q.limit(page * per_page).stream())

    total = len(all_docs)
    start = (page - 1) * per_page
    page_docs = all_docs[start : start + per_page]

    entries = []
    for doc in page_docs:
        data = doc.to_dict()
        if data:
            data.pop("markdown", None)  # Metadata only
            data["id"] = doc.id
            entries.append(data)

    return {
        "entries": entries,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


def list_library_sections() -> list[str]:
    """Return distinct sections from Firestore."""
    # Firestore doesn't have distinct queries. Scan and collect unique.
    docs = _client().collection(_COLLECTION).stream()
    sections: set[str] = set()
    for doc in docs:
        data = doc.to_dict()
        if data:
            sections.add(data.get("section", ""))
    return sorted(s for s in sections if s)


def list_library_tags() -> list[str]:
    """Return all distinct tags."""
    docs = _client().collection(_COLLECTION).stream()
    tags: set[str] = set()
    for doc in docs:
        data = doc.to_dict()
        if data:
            tags.update(data.get("tags", []))
    return sorted(tags)


def count_library_entries(section: str) -> int:
    """Count entries in a section."""
    docs = (
        _client()
        .collection(_COLLECTION)
        .where("section", "==", section)
        .stream()
    )
    return sum(1 for _ in docs)


def get_library_index() -> dict[str, Any]:
    """Build fresh index from Firestore entries.

    Previously this returned a cached document (library_index/latest)
    which could become stale after new saves. Now it always rebuilds
    from the library_entries collection to ensure consistency.
    """
    return _build_library_index_from_firestore()


def _build_library_index_from_firestore() -> dict[str, Any]:
    """Scan all entries and build index."""
    entries = []
    bundles = []
    docs = _client().collection(_COLLECTION).stream()

    for doc in docs:
        data = doc.to_dict()
        if data is None:
            continue
        record = {
            "title": data.get("title", ""),
            "path": data.get("path", ""),
            "section": data.get("section", ""),
            "category": data.get("category", ""),
            "status": data.get("status", ""),
            "type": data.get("type", ""),
            "source_url": data.get("source_url"),
            "updated_at": data.get("updated_at", datetime.now()).isoformat(),
        }
        if data.get("type") == "bundle-index":
            bundles.append(record)
        else:
            entries.append(record)

    index = {
        "generated_at": datetime.now().isoformat(),
        "entries": entries,
        "bundles": bundles,
    }

    # Cache it
    _client().collection(_INDEX_DOC).document("latest").set(index)
    return index
