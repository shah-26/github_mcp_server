# src/github_mcp_server/tools/commits.py
from typing import Any, Optional

from ..config import settings
from ..github_client import github_client


def list_recent_commits(
    repo: str,
    path: Optional[str] = None,
    since: Optional[str] = None,
    limit: int = settings.default_page_size,
) -> dict[str, Any]:
    """List recent commits for a repo, optionally scoped to a file/directory path.

    Args:
        repo: "owner/name", e.g. "facebook/react"
        path: optional file or directory to scope commits to
        since: optional ISO 8601 date, e.g. "2025-01-01T00:00:00Z"
        limit: max commits to return (capped at settings.max_page_size)
    """
    capped_limit = min(limit, settings.max_page_size)

    params: dict[str, Any] = {}
    if path:
        params["path"] = path
    if since:
        params["since"] = since

    raw_commits = github_client.get_paginated(
        f"/repos/{repo}/commits",
        params=params,
        per_page=capped_limit,
        max_items=capped_limit,
    )

    commits = [
        {
            "sha": c["sha"],
            "short_sha": c["sha"][:7],
            "author": (c.get("commit", {}).get("author", {}) or {}).get("name"),
            "date": (c.get("commit", {}).get("author", {}) or {}).get("date"),
            "message": (c.get("commit", {}).get("message", "") or "").split("\n")[0],
        }
        for c in raw_commits
    ]

    return {
        "repo": repo,
        "count": len(commits),
        "limit_applied": capped_limit,
        "commits": commits,
    }