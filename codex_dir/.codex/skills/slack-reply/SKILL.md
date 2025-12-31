---
name: slack-reply
description: >-
  Guidance for responding through Slack MCP: immediate acknowledgements, progress cadence,
  thread discipline, message templates, and failure handling. Use whenever Codex must reply
  to Slack mentions or share progress/results.
---

# Slack Reply Skill

This skill standardizes communication via Slack MCP. From task start to finish, always
reply in the same thread and share progress frequently.

## Prerequisites
- Use `slack_reply_to_thread` (or `slack_post_message` with `thread_ts`).
- `channel_id` and `thread_ts` are provided by FastAPI/Bolt; no need to re-fetch them.
- Do not include secrets; if necessary, say "shared separately".

## Immediate Acknowledgement Rules
1. When you receive a mention or question, **always reply in the same thread** and acknowledge receipt first.
2. Even if you cannot answer right away, state "starting work" and when you will report back.
3. If a task or verification takes longer than 1 hour, post an interim update.

## Progress Reporting Timing
1. **Task understanding**: summary, plan, open questions.
2. **Main changes done**: changed files, content, next action.
3. **Tests done**: command and result (or reason for not running).
4. **Final report**: change summary, commit/PR, TODOs, test status.
- For long work, add a short update every hour.

## Message Templates
```text
I understand the task. I will proceed as follows.
1. ...
2. ...
Let me know if anything is unclear.
```
```text
Progress update: <what was done> is complete. Next, I will work on <next step>.
```
```text
Done.
- Changes: ...
- Commit/PR: ...
- Tests: ...
Let me know if you need anything else.
```

## Errors / Delays
- If a Slack API or MCP issue occurs, summarize the response, report it, and ask whether to retry.
- If you cannot proceed (e.g., waiting for approval), state that and give the next ETA.

## Checklist
- [ ] Replied immediately in the instruction thread
- [ ] Shared progress at required timings plus hourly updates if long-running
- [ ] Clearly listed what was done and the next action
- [ ] Reported test results or the reason for not running
- [ ] Shared commit/PR info with link
