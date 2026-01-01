---
name: work-logger
description: >-
  Record per-task work logs into each work folder's SQLite DB and update the global
  work_index.db summary after meaningful steps. Use whenever work starts or finishes.
---

# Work Logger Skill

This skill records and references work logs in **each work folder's SQLite DB** and in the
**aggregate DB at the base folder**.

## Included Script
- `scripts/manage_work_logs.py` : ensure/insert/query for work_logs

## Target DBs
- Work folder: `work/<project>/work_logs.db` (auto-create if missing)
- Base folder: `work_index/work_index.db` (auto-create if missing)

## When to Record
- At work start (request received / folder chosen)
- After main changes
- When tests are run
- At completion (include reply summary)

## Fields to Record (work folder DB)
- `query`: summary of the user's request
- `action`: `start` / `update` / `test` / `finish`
- `detail`: what was done
- `slack_thread`: `channel_id:thread_ts`
- `outputs`: summary of PRs or deliverables
- `metadata`: extra info (JSON)

## Implementation Notes
- Use the script above for log insert/query; auto-create DB if missing.
- If schemas differ, extend `schema.sql` to align them.

## Example Usage
### Create/append a work log
```bash
python scripts/manage_work_logs.py ensure
python scripts/manage_work_logs.py insert \
  --query "Fix login screen" \
  --action update \
  --detail "Adjust validation in Login.tsx" \
  --slack-thread "CXXXX:123456.789" \
  --outputs "PR #12" \
  --metadata '{"branch":"codex/login-fix"}'
```

## Notes
- Do not store secrets in the DB.
- Store **summaries**, not full Slack conversations.
