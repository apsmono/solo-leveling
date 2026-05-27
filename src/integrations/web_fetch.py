"""
Web fetch module for enriching library entries from URLs.

Fetches metadata from external links so the brain can store structured,
searchable entries instead of raw URLs.

Supported platforms:
  - YouTube (via oEmbed — no API key)
  - GitHub repos (via existing GitHub client)
  - Generic web pages (title + meta description via HTML parsing)
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

_YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com", "youtube.com"}
_GITHUB_HOSTS = {"github.com", "www.github.com"}


def detect_platform(url: str) -> str:
    """Return platform key for a URL, or 'generic'."""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host in _YOUTUBE_HOSTS or host.endswith(".youtube.com"):
        return "youtube"
    if host in _GITHUB_HOSTS:
        return "github"
    return "generic"


# ---------------------------------------------------------------------------
# Unified fetch dispatcher
# ---------------------------------------------------------------------------

def fetch_url_metadata(url: str) -> dict[str, Any]:
    """Fetch metadata for any supported URL.

    Returns a normalized dict with keys:
      - title (str)
      - description (str)
      - author (str)
      - platform (str)
      - source_url (str)
      - extra (dict)
    """
    platform = detect_platform(url)
    try:
        if platform == "youtube":
            return _fetch_youtube_metadata(url)
        if platform == "github":
            return _fetch_github_repo_metadata(url)
        return _fetch_generic_metadata(url)
    except Exception as exc:
        logger.warning("Failed to fetch metadata for %s: %s", url, exc)
        return _fallback_metadata(url, platform)


# ---------------------------------------------------------------------------
# YouTube (oEmbed — no API key required)
# ---------------------------------------------------------------------------

def _fetch_youtube_metadata(url: str) -> dict[str, Any]:
    """Fetch YouTube video metadata via oEmbed."""
    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        response = client.get(oembed_url)
        response.raise_for_status()
        data = response.json()

    return {
        "title": data.get("title", ""),
        "description": "",
        "author": data.get("author_name", ""),
        "platform": "youtube",
        "source_url": url,
        "extra": {
            "thumbnail_url": data.get("thumbnail_url", ""),
            "thumbnail_width": data.get("thumbnail_width"),
            "thumbnail_height": data.get("thumbnail_height"),
            "provider_name": data.get("provider_name", "YouTube"),
            "type": data.get("type", "video"),
        },
    }


# ---------------------------------------------------------------------------
# GitHub repo
# ---------------------------------------------------------------------------

def _fetch_github_repo_metadata(url: str) -> dict[str, Any]:
    """Fetch GitHub repository metadata via the existing GitHub client."""
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        return _fallback_metadata(url, "github")

    owner, repo_name = path_parts[0], path_parts[1]
    repo = f"{owner}/{repo_name}"

    try:
        from src.integrations.github import client as gh
        result = gh.health_check()
        if not result.get("ok"):
            return _fallback_metadata(url, "github")

        info = gh._request("GET", f"/repos/{repo}")
        return {
            "title": info.get("full_name", repo),
            "description": info.get("description", ""),
            "author": info.get("owner", {}).get("login", owner),
            "platform": "github",
            "source_url": url,
            "extra": {
                "stars": info.get("stargazers_count"),
                "language": info.get("language"),
                "topics": info.get("topics", []),
                "forks": info.get("forks_count"),
                "open_issues": info.get("open_issues_count"),
                "license": info.get("license", {}).get("name") if info.get("license") else None,
                "default_branch": info.get("default_branch"),
            },
        }
    except Exception as exc:
        logger.warning("GitHub fetch failed for %s: %s", url, exc)
        return _fallback_metadata(url, "github")


# ---------------------------------------------------------------------------
# Generic web page
# ---------------------------------------------------------------------------

def _fetch_generic_metadata(url: str) -> dict[str, Any]:
    """Fetch generic HTML page and extract title + meta description."""
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        response = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        text = response.text

    title = _extract_html_title(text) or ""
    description = _extract_meta_description(text) or ""

    # Fallback: use URL path last segment as title
    if not title:
        path = urlparse(url).path.strip("/")
        title = path.split("/")[-1].replace("-", " ").replace("_", " ").title() if path else url

    return {
        "title": title,
        "description": description,
        "author": "",
        "platform": "generic",
        "source_url": url,
        "extra": {
            "content_type": response.headers.get("content-type", ""),
        },
    }


def _extract_html_title(html: str) -> Optional[str]:
    match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE | re.DOTALL)
    if match:
        return re.sub(r"\s+", " ", match.group(1)).strip()
    return None


def _extract_meta_description(html: str) -> Optional[str]:
    # Try og:description first, then meta description
    patterns = [
        r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']',
        r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:description["\']',
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
        r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------

def _fallback_metadata(url: str, platform: str) -> dict[str, Any]:
    return {
        "title": url,
        "description": "",
        "author": "",
        "platform": platform,
        "source_url": url,
        "extra": {},
    }
