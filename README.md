# GitHub MCP Server

A Python-based Model Context Protocol (MCP) server that exposes GitHub repository activity to AI clients in a clean, read-only, structured format.

This project was built to make GitHub context retrieval easy for AI-powered tools and agents. Instead of manually querying the GitHub API, an MCP client can ask for recent commit activity, scoped to a repository, file, or time window.

## Why this project matters

In modern AI workflows, context is everything. This project helps provide historical code context from GitHub so an assistant can answer questions like:

- What changed recently in this repository?
- Who touched this file most recently?
- What shipped before a specific date or bug window?
- What commit activity exists around a particular directory?

The server is intentionally read-only and designed for safe information retrieval.

## What I built

### Read-only MCP tool for GitHub commit history
The project exposes a server tool named `list_recent_commits` that accepts:

- `repo` — repository in the format `owner/name`
- `path` — optional file or directory path to scope results
- `since` — optional ISO 8601 date filter
- `limit` — maximum number of commits to return

It returns structured commit metadata including:

- commit SHA
- short SHA
- author name
- commit date
- commit message headline

### GitHub API integration layer
I implemented a dedicated GitHub client wrapper that:

- authenticates requests using a GitHub token
- sends requests with the GitHub REST API headers
- handles pagination automatically
- supports safe result limiting
- centralizes API access instead of scattering requests across the codebase

### Production-minded error handling
The project includes explicit error classes for:

- authentication failures
- missing resources
- rate limiting
- upstream API issues and network failures

This makes the server more robust and easier to integrate with downstream AI tools.

### Environment-based configuration
The project loads configuration from environment variables and `.env`, allowing secure setup for GitHub credentials and runtime defaults without hardcoding secrets.

## Tech stack

- Python 3.11
- Model Context Protocol (MCP)
- HTTPX for API requests
- GitHub REST API
- Python-dotenv for environment configuration

## Project structure

- `src/github_mcp_server/server.py` — MCP server setup and tool registration
- `src/github_mcp_server/tools/commits.py` — commit retrieval logic
- `src/github_mcp_server/github_client.py` — GitHub API client and pagination logic
- `src/github_mcp_server/config.py` — environment/config management
- `src/github_mcp_server/errors.py` — structured error handling
- `tests/test_commits.py` — commit-related test scaffolding

## Example tool usage

```python
list_recent_commits(
    repo="microsoft/vscode",
    path="src",
    since="2025-01-01T00:00:00Z",
    limit=10,
)
```

### Example response

```json
{
  "repo": "microsoft/vscode",
  "count": 2,
  "limit_applied": 10,
  "commits": [
    {
      "sha": "abc123def456",
      "short_sha": "abc123d",
      "author": "Jane Developer",
      "date": "2025-01-15T10:22:00Z",
      "message": "Improve repository search performance"
    }
  ]
}
```

## How to run

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set the required environment variable:

```bash
export GITHUB_TOKEN=your_github_token
```

4. Start the MCP server:

```bash
python -m github_mcp_server.server
```

## What this demonstrates

This project reflects practical software engineering skills in:

- API integration
- Python backend development
- AI tooling integration via MCP
- secure configuration management
- structured error handling
- working with data from external services
- building lightweight, focused developer tools

## Summary

This project is a focused example of building an AI-readable, GitHub-aware backend service that delivers relevant repository history in a structured, safe, and reusable way. It combines API integration, Python engineering, and AI tool interoperability into a compact, real-world project.
