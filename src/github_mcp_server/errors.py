# src/github_mcp_server/errors.py
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GitHubMCPError(Exception):
    """Base class for all errors this server raises intentionally.

    Carries enough structure that server.py can convert it into a
    clean, consistent MCP tool error response without inspecting
    exception messages or guessing.
    """
    code: str            # short machine-readable code, e.g. "not_found"
    message: str         # human/agent-readable explanation
    http_status: Optional[int] = None
    retry_after_seconds: Optional[int] = None

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class NotFoundError(GitHubMCPError):
    def __init__(self, resource: str):
        super().__init__(
            code="not_found",
            message=f"{resource} was not found. Check the repo/path/sha and try again.",
            http_status=404,
        )


class AuthError(GitHubMCPError):
    def __init__(self):
        super().__init__(
            code="auth_error",
            message=(
                "GitHub authentication failed. The server's token is invalid "
                "or expired — this is a server configuration issue, not something "
                "the caller can fix."
            ),
            http_status=401,
        )


class RateLimitError(GitHubMCPError):
    def __init__(self, retry_after_seconds: Optional[int] = None):
        super().__init__(
            code="rate_limited",
            message=(
                f"GitHub API rate limit exceeded. Retry after "
                f"{retry_after_seconds} seconds." if retry_after_seconds
                else "GitHub API rate limit exceeded. Try again later."
            ),
            http_status=403,
            retry_after_seconds=retry_after_seconds,
        )


class UpstreamError(GitHubMCPError):
    """Catch-all for unexpected GitHub API failures (5xx, network issues)."""
    def __init__(self, detail: str, http_status: Optional[int] = None):
        super().__init__(
            code="upstream_error",
            message=f"Unexpected error calling GitHub API: {detail}",
            http_status=http_status,
        )