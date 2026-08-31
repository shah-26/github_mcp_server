# src/github_mcp_server/server.py
import logging
import sys

from mcp.server.fastmcp import FastMCP

from .tools.commits import list_recent_commits as _list_recent_commits

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    stream=sys.stderr,  # stdout is reserved for MCP protocol messages
)
logger = logging.getLogger("github_mcp_server")

mcp = FastMCP("github-context-server")


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
    }
)
def list_recent_commits(
    repo: str,
    path: str | None = None,
    since: str | None = None,
    limit: int = 10,
) -> dict:
    """Find recent commits in a GitHub repository, optionally scoped to a
    specific file or directory. Use this to investigate what changed
    recently — e.g. "what shipped before this bug appeared" or "who
    touched this file lately." Returns commit summaries (sha, author,
    date, message headline) only — NOT full diffs. Use get_commit_detail
    if you need to see the actual file changes for a specific commit.

    Args:
        repo: Repository in "owner/name" format, e.g. "facebook/react".
        path: Optional file or directory path to scope results to,
            e.g. "src/index.js".
        since: Optional ISO 8601 timestamp, e.g. "2025-01-01T00:00:00Z".
            Only commits after this date are returned.
        limit: Max commits to return. Default 10, capped at 50.
    """
    logger.info(f"list_recent_commits called: repo={repo}, path={path}, limit={limit}")
    try:
        result = _list_recent_commits(repo=repo, path=path, since=since, limit=limit)
        logger.info(f"list_recent_commits succeeded: {result['count']} commits returned")
        return result
    except Exception as exc:
        logger.error(f"list_recent_commits failed: {exc}")
        raise


if __name__ == "__main__":
    mcp.run(transport="streamable-http")