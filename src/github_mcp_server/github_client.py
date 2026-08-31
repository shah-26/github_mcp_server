# src/github_mcp_server/github_client.py
import time
from typing import Any, Optional

import httpx

from .config import settings
from .errors import AuthError, GitHubMCPError, NotFoundError, RateLimitError, UpstreamError


class GitHubClient:
    """Thin wrapper around GitHub's REST API.

    This is the ONLY place in the codebase that knows about GitHub's
    actual HTTP shape (URLs, headers, status codes). Tools never call
    httpx directly — they call methods on this class.
    """

    def __init__(self) -> None:
        self._client = httpx.Client(
            base_url=settings.github_api_base_url,
            headers={
                "Authorization": f"Bearer {settings.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=settings.request_timeout_seconds,
        )

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        """GET a GitHub API path, returning parsed JSON or raising a GitHubMCPError."""
        try:
            response = self._client.get(path, params=params)
        except httpx.TimeoutException:
            raise UpstreamError(detail="Request to GitHub API timed out.")
        except httpx.RequestError as exc:
            raise UpstreamError(detail=f"Network error: {exc}")

        return self._handle_response(response, resource_hint=path)

    def _handle_response(self, response: httpx.Response, resource_hint: str) -> Any:
        if response.status_code == 200:
            return response.json()

        if response.status_code == 401:
            raise AuthError()

        if response.status_code == 404:
            raise NotFoundError(resource=resource_hint)

        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining == "0":
                reset_ts = response.headers.get("X-RateLimit-Reset")
                retry_after = (
                    max(0, int(reset_ts) - int(time.time())) if reset_ts else None
                )
                raise RateLimitError(retry_after_seconds=retry_after)
            raise GitHubMCPError(
                code="permission_denied",
                message=f"Token does not have access to: {resource_hint}",
                http_status=403,
            )

        # Anything else (5xx, unexpected 4xx) — catch-all
        raise UpstreamError(
            detail=f"GitHub returned {response.status_code}: {response.text[:200]}",
            http_status=response.status_code,
        )


    def get_paginated(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
        per_page: int = 10,
        max_items: int = 50,
    ) -> list[Any]:
        """GET a paginated GitHub list endpoint, following Link headers
        until max_items is reached or there are no more pages.
        """
        params = dict(params or {})
        params["per_page"] = min(per_page, max_items)

        items: list[Any] = []
        url: Optional[str] = path

        while url and len(items) < max_items:
            try:
                response = self._client.get(url, params=params if url == path else None)
            except httpx.TimeoutException:
                raise UpstreamError(detail="Request to GitHub API timed out.")
            except httpx.RequestError as exc:
                raise UpstreamError(detail=f"Network error: {exc}")

            page_items = self._handle_response(response, resource_hint=path)
            items.extend(page_items)

            url = self._next_page_url(response)
            params = None  # next URL already has query params baked in

        return items[:max_items]

    @staticmethod
    def _next_page_url(response: httpx.Response) -> Optional[str]:
        """Parse the Link header for a 'next' page URL, GitHub's standard pagination format."""
        link_header = response.headers.get("Link")
        if not link_header:
            return None
        for part in link_header.split(","):
            segment = part.strip()
            if 'rel="next"' in segment:
                return segment.split(";")[0].strip().strip("<>")
        return None

github_client = GitHubClient()