"""
YouTube-specific utilities for resource link ingestion.

Extracts video IDs from various YouTube URL formats and fetches
transcripts when available.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Video ID extraction
# ---------------------------------------------------------------------------

def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from common URL formats.

    Supports:
      - youtube.com/watch?v=VIDEO_ID
      - youtu.be/VIDEO_ID
      - youtube.com/shorts/VIDEO_ID
      - youtube.com/embed/VIDEO_ID
      - m.youtube.com/watch?v=VIDEO_ID
    """
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/|youtube\.com/embed/|m\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})",
        r"[?&]v=([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


# ---------------------------------------------------------------------------
# Transcript fetching
# ---------------------------------------------------------------------------

def fetch_transcript(video_id: str) -> Optional[str]:
    """Fetch auto-generated transcript for a YouTube video.

    Returns the transcript as plain text, or None if unavailable.
    Gracefully handles: private videos, disabled captions, region blocks.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        lines = [entry["text"] for entry in transcript_list]
        return "\n".join(lines)
    except Exception as exc:
        logger.warning("Transcript unavailable for %s: %s", video_id, type(exc).__name__)
        return None
