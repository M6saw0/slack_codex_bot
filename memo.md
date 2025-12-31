# Coding from Your Phone with Slack x Codex CLI x GitHub

Codex on Slack is super convenient.
Whether you're on the train or in bed, you can just say "please fix this" and the AI handles it. Pure magic.

But after using it for a while, you'll hit the "almost!" moments.

*   "I want you to run tests in a Docker environment..."
*   "I need to run heavy workloads on a GPU machine..."
*   "I want you to directly edit files on my PC..."

With Codex on Slack (cloud), you can't really use the power or environment of your strongest local machine.

**So why not control the Codex CLI on your home PC from Slack?**

That's exactly what we built here:
"Mention from Slack on your phone -> your home PC runs with Docker/GPU -> PR created on GitHub"
All fully automated.

---

## 0. What are we building?

Here is the overall picture:

```text
📱 Phone (Slack)
   │
   │ "@codex-bot please fix validation and run tests!"
   │
☁️ Slack Cloud
   │
   │ (Connected via Socket Mode)
   │
🏠 Home PC (WSL2 / Linux / Mac)
   │
   ├── 🐍 Python bot (app-socket.py)
   │     │  - Detects mentions
   │     │  - "Summons" Codex CLI (subprocess)
   │     │
   └── 🤖 Codex CLI
         │  - Codes as instructed
         ├── 💬 Slack MCP  (posts progress in thread)
         └── 🐙 GitHub MCP (edit -> commit -> PR)
```

---

## 1. What you need

### Must-haves
*   **Slack workspace**: permissions to create an app
*   **GitHub account**: able to create a PAT (Personal Access Token)
*   **Home PC**: Python environment (examples assume **WSL2**, but Mac/Linux is OK)
*   **Codex CLI**: installed
*   **Node.js**: `npx` must be available (to run MCP servers)

### Nice-to-haves
*   **Docker**: required if you want tests in containers
*   **GPU / CUDA**: required if you want to run heavy AI workloads

---

## 2. Slack app setup (the hardest part)

This is the only truly annoying section. You got this.

### 2-1. Create the app
1.  Go to [Slack API: Your Apps](https://api.slack.com/apps).
2.  Click **Create New App** -> **From scratch**.
3.  Name it something like `codex-bot` and choose your workspace.

### 2-2. Enable Socket Mode
Instead of exposing an external URL, the app connects via WebSocket.
1.  Left menu **Socket Mode** -> turn **Enable Socket Mode** ON.
2.  Create a token with a name (e.g., `socket-token`) and click **Generate**.
3.  You will see a token starting with `xapp-`.
    -> **This is `SLACK_APP_TOKEN`. Save it.**

### 2-3. Add scopes (permissions)
Define what the bot can do.
1.  Left menu **OAuth & Permissions**.
2.  Add the following to **Bot Token Scopes**:
    *   `app_mentions:read` (to react to mentions)
    *   `chat:write` (to reply)
3.  Click **Install to Workspace** at the top.
4.  You will see a token starting with `xoxb-`.
    -> **This is `SLACK_BOT_TOKEN`. Save it.**

### 2-4. Find your team ID
You need the workspace/team ID to use Slack MCP.
Run this in your terminal:

```bash
curl -X POST https://slack.com/api/auth.test \
  -H "Authorization: Bearer xoxb-..."
```

In the response, find something like:

```text
"team_id": "T0xxxxxx"
```

Save the `T0...` value. This is `SLACK_TEAM_ID`.

---

## 3. Create a GitHub token

This is the key that lets the AI edit code and create PRs on your behalf.

1.  GitHub settings -> **Developer settings** -> **Personal access tokens** -> **Fine-grained tokens**.
2.  Click **Generate new token**.
3.  **Repository access**: choose the repo (or **All repositories**).
4.  **Permissions**:
    *   `Contents`: Read and write
    *   `Pull requests`: Read and write
    *   `Issues`: Read and write
5.  Create the token and save it (`github_pat_...`).
    -> **This is `GITHUB_PERSONAL_ACCESS_TOKEN`.**

---

## 4. Configure Codex CLI

Give Codex "the ability to write to Slack" and "the ability to operate GitHub".
Edit `~/.codex/config.toml` (create it if it does not exist).

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

Replace `xoxb-...`, `T0...`, `github_pat_...` with your actual values.

---

## 5. The summoning ritual (setup)

From here, work in the actual repo you want Codex to operate on.

### 5-1. Prepare a session
Codex keeps conversation history. Since we want a dedicated agent for this repo, create a session once by hand.

Run this in the target project folder:
```bash
codex exec --full-auto "Initialize as the Slack/GitHub-connected agent dedicated to this repository..."
```

Notes:

- `--full-auto` allows automatic decisions during execution (file edits, commands, etc.).
- The first run may take a while (plans/logs appear and it can be slow).

When it finishes, save the **SESSION_ID** it prints.

### 5-2. Create the relay bot
We recommend a separate folder (e.g., `~/tools/codex-bot`) from the project you want Codex to operate.

Create a `.env` file and write all collected tokens:

```bash
# .env
# Path to the project folder that Codex should operate on (absolute path recommended)
CODEX_ACTION_FOLDER=/home/user/my-project
# The fixed session ID from step 5-1
CODEX_SESSION_ID=xxxx-xxxx-...
# Slack Socket Mode Token (xapp-...)
SLACK_APP_TOKEN=xapp-...
# Slack Bot Token (xoxb-...)
SLACK_BOT_TOKEN=xoxb-...
```

Next, place the bot source `app-socket.py`:

```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os, subprocess

from dotenv import load_dotenv
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
CODEX_ACTION_FOLDER = os.getenv("CODEX_ACTION_FOLDER")
CODEX_SESSION_ID = os.getenv("CODEX_SESSION_ID")
app = App(token=SLACK_BOT_TOKEN)  # xoxb-...

# Runs when mentioned
@app.event("app_mention")
def handle_app_mention(body, say):
    event = body["event"]
    text = event.get("text", "")
    channel = event["channel"]
    thread_ts = event.get("thread_ts") or event.get("ts")

    # Remove the mention part
    parts = text.split(maxsplit=1)
    user_text = parts[1].strip() if len(parts) == 2 and parts[0].startswith("<@") else text.strip()
    if not user_text:
        return

    prompt = (
        f"Slack channel_id={channel}, thread_ts={thread_ts}. "
        f"Use Slack MCP to post progress and results to this thread, "
        f"and use GitHub MCP to make code changes, run tests, commit, and open a PR. "
        f"User request: {user_text}"
    )

    subprocess.Popen(
        ["codex", "exec", "resume", CODEX_SESSION_ID, prompt],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=CODEX_ACTION_FOLDER,  # Run in the Codex action folder
    )

    # Note:
    # stdout/stderr are sent to DEVNULL so Slack event logs are not flooded
    # with Codex output (keeping the bot quiet).

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)  # xapp-...
    handler.start()
```

### 5-3. Launch

```bash
# Create venv and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install slack-bolt python-dotenv

# Start the bot
python app-socket.py
```

If you see `⚡️ Bolt app is running!`, it's working.
Your PC is now waiting for commands from Slack.

---

## 6. Put it to use

Grab your phone, lean back, and post a coding request in Slack.

(First time only, Slack may ask you to add the bot to the channel.)

```text
@codex-bot Fix the login validation, run Docker tests, and open a PR if it passes!
```

Then...

1.  **Your home PC** starts running.
2.  **Slack** replies in the thread: "Got it, starting work."
3.  After a while: "Fix is done. Tests passed. PR: https://github.com/..."

**So good.**

---

## Future ideas

Once this works, you can keep customizing:

*   **Automation**: Run `app-socket.py` as a service (systemd / Task Scheduler).
*   **Session management**: Instead of a fixed session ID, create a new session per thread (or rotate when tokens are used up). Going further, add a memory layer so new sessions can reuse context.
*   **Security**: Restrict to specific channels or specific users.

Build your own ultimate dev partner and have fun.
