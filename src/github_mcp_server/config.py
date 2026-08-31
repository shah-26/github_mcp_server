# src/github_mcp_server/config.py
import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    github_token: str
    github_api_base_url: str
    default_page_size: int
    max_page_size: int
    diff_full_mode_line_cap: int
    request_timeout_seconds: float


def load_settings() -> Settings:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.stderr.write(
            "FATAL: GITHUB_TOKEN environment variable is not set. "
            "The server cannot start without it.\n"
        )
        sys.exit(1)

    return Settings(
        github_token=token,
        github_api_base_url=os.environ.get(
            "GITHUB_API_BASE_URL", "https://api.github.com"
        ),
        default_page_size=int(os.environ.get("DEFAULT_PAGE_SIZE", "10")),
        max_page_size=int(os.environ.get("MAX_PAGE_SIZE", "50")),
        diff_full_mode_line_cap=int(os.environ.get("DIFF_FULL_MODE_LINE_CAP", "500")),
        request_timeout_seconds=float(os.environ.get("REQUEST_TIMEOUT_SECONDS", "10")),
    )


settings = load_settings()