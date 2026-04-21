"""
Google Drive integration client.

Provides read and write access to Google Drive files and folders.
Uses the Google Drive API v3 via a service account or OAuth2 credentials.

Environment variables required:
    GOOGLE_CREDENTIALS_PATH  — path to service_account.json or oauth2_credentials.json

Usage:
    from src.integrations.gdrive.client import list_files, read_doc, create_doc
"""

from __future__ import annotations

import os
import logging
from typing import Any

from google.oauth2 import service_account  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",   # create/update files the app owns
]


def _service():
    """Build and return an authenticated Google Drive API service."""
    creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH")
    if not creds_path:
        raise EnvironmentError(
            "GOOGLE_CREDENTIALS_PATH is not set. "
            "Download a service account key from Google Cloud Console and set the path in .env."
        )
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

def list_files(folder_id: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    """
    List files in Google Drive (or in a specific folder).
    Returns a list of simplified dicts: {id, name, mimeType, webViewLink}.
    """
    query = f"'{folder_id}' in parents and trashed=false" if folder_id else "trashed=false"
    response = (
        _service()
        .files()
        .list(
            q=query,
            pageSize=limit,
            fields="files(id, name, mimeType, webViewLink)",
        )
        .execute()
    )
    files = response.get("files", [])
    logger.info("Listed %d files from Google Drive.", len(files))
    return files


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def read_doc(file_id: str) -> str:
    """
    Export a Google Doc as plain text and return its content.
    For non-Google-Doc files, returns a message to use download instead.
    """
    try:
        content = (
            _service()
            .files()
            .export(fileId=file_id, mimeType="text/plain")
            .execute()
        )
        if isinstance(content, bytes):
            return content.decode("utf-8")
        return str(content)
    except HttpError as e:
        if e.resp.status == 403:
            return f"Cannot export file {file_id}: not a Google Doc or missing permission."
        raise


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_doc(name: str, content: str, folder_id: str | None = None) -> dict[str, Any]:
    """
    Create a new Google Doc with the given name and plain-text content.
    Returns the created file metadata: {id, name, webViewLink}.
    """
    service = _service()

    # Create the file metadata
    metadata: dict[str, Any] = {
        "name": name,
        "mimeType": "application/vnd.google-apps.document",
    }
    if folder_id:
        metadata["parents"] = [folder_id]

    # Create empty doc first
    file = service.files().create(body=metadata, fields="id, name, webViewLink").execute()
    file_id = file["id"]

    # Write content by uploading plain-text media
    from googleapiclient.http import MediaInMemoryUpload  # type: ignore

    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain", resumable=False)
    service.files().update(
        fileId=file_id,
        media_body=media,
    ).execute()

    logger.info("Created Google Doc '%s' (id=%s).", name, file_id)
    return file


# ---------------------------------------------------------------------------
# Move / rename
# ---------------------------------------------------------------------------

def move_file(file_id: str, new_folder_id: str) -> None:
    """Move a file to a different folder."""
    # Retrieve current parents
    file = _service().files().get(fileId=file_id, fields="parents").execute()
    previous_parents = ",".join(file.get("parents", []))
    _service().files().update(
        fileId=file_id,
        addParents=new_folder_id,
        removeParents=previous_parents,
        fields="id, parents",
    ).execute()
    logger.info("Moved file %s to folder %s.", file_id, new_folder_id)
