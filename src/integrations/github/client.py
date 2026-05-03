"""
GitHub API client for cross-repo orchestration.

Requires GITHUB_PAT environment variable (fine-grained personal access token).
Recommended token scopes: repo (read), issues (write), actions (write).
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.core.config import GITHUB_PAT

logger = logging.getLogger(__name__)

API_BASE = "https://api.github.com"


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "solo-leveling-brain",
    }


def _request(method: str, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute an authenticated GitHub API request."""
    if not GITHUB_PAT:
        raise EnvironmentError("GITHUB_PAT is not set. Add it to your .env file.")

    url = f"{API_BASE}{path}"
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.request(method, url, headers=_headers(), json=json)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error("GitHub API error: %s %s — %s", method, path, e.response.text)
        raise
    except Exception:
        logger.exception("GitHub API request failed: %s %s", method, path)
        raise


# ---------------------------------------------------------------------------
# Repos
# ---------------------------------------------------------------------------

def list_repos(visibility: str = "all", per_page: int = 10) -> list[dict[str, Any]]:
    """List repositories for the authenticated user."""
    data = _request("GET", f"/user/repos?visibility={visibility}&per_page={per_page}&sort=updated")
    return [
        {
            "name": r["full_name"],
            "url": r["html_url"],
            "private": r["private"],
            "updated_at": r["updated_at"],
        }
        for r in data
    ]


def get_repo(repo: str) -> dict[str, Any]:
    """Get metadata for a repository. Format: 'owner/repo'."""
    r = _request("GET", f"/repos/{repo}")
    return {
        "name": r["full_name"],
        "url": r["html_url"],
        "description": r.get("description", ""),
        "stars": r["stargazers_count"],
        "language": r.get("language", ""),
        "default_branch": r["default_branch"],
    }


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

def create_issue(repo: str, title: str, body: str = "") -> dict[str, Any]:
    """Create an issue in a repository. Format: 'owner/repo'."""
    payload = {"title": title, "body": body}
    r = _request("POST", f"/repos/{repo}/issues", json=payload)
    return {
        "number": r["number"],
        "title": r["title"],
        "url": r["html_url"],
        "state": r["state"],
    }


# ---------------------------------------------------------------------------
# Actions (workflows)
# ---------------------------------------------------------------------------

def list_workflows(repo: str) -> list[dict[str, Any]]:
    """List workflow definitions in a repository."""
    data = _request("GET", f"/repos/{repo}/actions/workflows")
    return [
        {
            "id": w["id"],
            "name": w["name"],
            "path": w["path"],
            "state": w["state"],
        }
        for w in data.get("workflows", [])
    ]


def trigger_workflow(repo: str, workflow_id: str | int, branch: str = "main") -> dict[str, Any]:
    """Trigger a workflow run on a branch."""
    payload = {"ref": branch}
    _request("POST", f"/repos/{repo}/actions/workflows/{workflow_id}/dispatches", json=payload)
    return {"status": "triggered", "repo": repo, "workflow": workflow_id, "branch": branch}


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def health_check() -> dict[str, Any]:
    """Return a lightweight health check result."""
    if not GITHUB_PAT:
        return {"ok": False, "error": "GITHUB_PAT not configured"}
    try:
        r = _request("GET", "/user")
        return {"ok": True, "user": r.get("login", "unknown")}
    except Exception as e:
        return {"ok": False, "error": str(e)}
