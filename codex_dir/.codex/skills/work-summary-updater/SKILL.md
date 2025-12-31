---
name: work-summary-updater
description: >-
  Update work_index/index.json and index.json based on recent work folder activity
  and work_index.db. Use at the end of a task.
---

# Work Summary Updater Skill

This skill covers routing decisions at the start of work and the **index.json (single source of truth)** update at completion.

## Targets
- `work_index/index.json` (single source of truth)
- `index.json` (top-level summary)

## Included Script
- `scripts/manage_work_index.py` : ensure/upsert/query for work_index

## Routing Steps
1. Summarize the instruction and extract key keywords.
2. Match against `keywords` / `query_patterns` in `index.json`.
3. Select the best-matching work folder.
4. If multiple candidates or unclear, confirm via Slack.
5. If none match, create `work/<short-name>`.

## Update Policy
- Keep `index.json` aligned with the latest user request and repo status.

## Update Steps
1. Read the latest record in `work_index/work_index.db`.
2. Organize `summary` / `tags` / `query_patterns` for the target folder.
3. Update `index.json` (single source of truth; reflect latest request/status).

## Format Rules
- `index.json` must include `folder` / `summary` / `keywords` / `query_patterns` / `last_used`.

## Notes
- `index.json` is the single source of truth.
- Keep JSON valid (no trailing commas).

## Example
```bash
python scripts/manage_work_index.py ensure
python scripts/manage_work_index.py upsert \
  --folder "work/20251231_slack_codex_bot" \
  --summary "Slack-controlled Codex CLI bot repo" \
  --keywords "slack,codex,bot,github" \
  --query-patterns "slack.*codex,slack bot" \
  --last-used "2025-12-31"
```
