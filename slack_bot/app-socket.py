from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import json
import os
import subprocess

from dotenv import load_dotenv
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
CODEX_ACTION_FOLDER = os.getenv("CODEX_ACTION_FOLDER")
app = App(token=SLACK_BOT_TOKEN)  # xoxb-...

def _history_limit() -> int:
    raw = os.getenv("SLACK_HISTORY_LIMIT", "50")
    try:
        value = int(raw)
    except ValueError:
        return 50
    return max(1, value)

def _fetch_recent_history(client, channel_id: str, thread_ts: str | None, limit: int):
    if thread_ts:
        resp = client.conversations_replies(channel=channel_id, ts=thread_ts, limit=limit)
        messages = resp.get("messages", [])
    else:
        resp = client.conversations_history(channel=channel_id, limit=limit)
        messages = resp.get("messages", [])

    formatted = []
    for msg in messages:
        formatted.append({
            "ts": msg.get("ts"),
            "thread_ts": msg.get("thread_ts") or msg.get("ts"),
            "user": msg.get("user"),
            "bot_id": msg.get("bot_id"),
            "subtype": msg.get("subtype"),
            "text": msg.get("text"),
        })
    return formatted

# Runs when mentioned
@app.event("app_mention")
def handle_app_mention(body, say, client):
    event = body["event"]
    text = event.get("text", "")
    channel = event["channel"]
    event_thread_ts = event.get("thread_ts")
    thread_ts = event_thread_ts or event.get("ts")

    print(f"user_text: {text}")

    # Remove the mention part
    parts = text.split(maxsplit=1)
    user_text = parts[1].strip() if len(parts) == 2 and parts[0].startswith("<@") else text.strip()
    if not user_text:
        return

    history_limit = _history_limit()
    recent_messages = _fetch_recent_history(client, channel, event_thread_ts, history_limit)
    history_json = json.dumps(recent_messages, ensure_ascii=False)

    prompt = (
        f"Slack channel_id={channel}, thread_ts={thread_ts}. "
        f"Use Slack MCP to post progress and results to this thread, "
        f"and use GitHub MCP to make code changes, run tests, commit, and open a PR. "
        f"Slack recent_messages(limit={history_limit}): {history_json}"
        f"User request: {user_text}"
    )

    subprocess.Popen(
        ["codex", "exec", "--full-auto", prompt],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=CODEX_ACTION_FOLDER,  # Run in the Codex action folder
    )

if __name__ == "__main__":
    print("Start App")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)  # xapp-...
    handler.start()
