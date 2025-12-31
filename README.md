# Slack Codex Bot

## Overview

This repository provides a simple relay that lets you trigger Codex CLI from Slack mentions. A Slack Socket Mode bot (`slack_bot/app-socket.py`) listens for `@codex-bot` mentions, builds a prompt with recent thread context, and launches Codex CLI to work inside the local project folder. Codex then posts progress back to the same Slack thread via the Slack MCP server and performs code changes/PRs via the GitHub MCP server.

**Repository layout**

- `codex_dir/`: The actual working folder for Codex CLI. This is where Codex runs commands and edits files.
- `slack_bot/`: The Python Socket Mode app that receives Slack mentions and launches Codex CLI.

## Usage

### 1) Prerequisites

- Slack app with Socket Mode enabled.
- Slack bot token (`SLACK_BOT_TOKEN`) and app token (`SLACK_APP_TOKEN`).
- GitHub Personal Access Token with repo permissions for the GitHub MCP server.
- Codex CLI installed and configured.
- Node.js (for MCP server execution via `npx`).

### 2) Configure Codex MCP servers

Edit `~/.codex/config.toml` (or create it if missing):

```toml
sandbox_mode = "workspace-write"

[features]
streamable_shell = true
web_search_request = true

# Slack MCP: progress reports
[mcp_servers.slack]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-slack"]
env = { SLACK_BOT_TOKEN = "xoxb-...", SLACK_TEAM_ID = "T0..." }

# GitHub MCP: code operations
[mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
env = { GITHUB_PERSONAL_ACCESS_TOKEN = "github_pat_..." }
```

Replace the placeholders with your real tokens/IDs.

### 3) Configure the Slack bot environment

Create `slack_bot/.env`:

```bash
# Slack tokens
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...

# Folder where Codex will run (this repo's codex_dir)
CODEX_ACTION_FOLDER=/absolute/path/to/this/repo/codex_dir

# Optional: how many recent messages to include in the prompt
SLACK_HISTORY_LIMIT=50
```

### 4) Install Python dependencies and run the bot

```bash
cd slack_bot
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install slack-bolt python-dotenv

python app-socket.py
```

When you see `Start App`, the bot is running.

### 5) Use it from Slack

Mention the bot in a channel the app is invited to:

```text
@codex-bot Fix the login validation and run tests, then open a PR.
```

The bot will:

1. Collect recent thread messages (if any).
2. Launch Codex CLI with a prompt that includes the Slack thread context.
3. Codex posts progress and results back into the same thread.

## Notes about the current Python implementation

The current `slack_bot/app-socket.py` differs from older examples:

- It runs `codex exec --full-auto` directly (no fixed session ID).
- It injects recent Slack history into the prompt using `SLACK_HISTORY_LIMIT`.

If you update the Python bot, keep the README in sync with its behavior.
