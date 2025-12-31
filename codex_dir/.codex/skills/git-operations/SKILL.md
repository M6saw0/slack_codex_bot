---
name: git-operations
description: >-
  Workflow for using GitHub MCP + git to create private repos, sync main via git switch,
  branch safely, push without touching main, and open PRs. Use for any task that needs
  Git branching/publishing guidance.
---

# Git Operations Skill

Use this skill to standardize operations with GitHub MCP and local `git`. All required
steps are documented here.

## Prerequisites
- You can call GitHub MCP `create_repository` (PAT configured).
- `git switch` is available locally (use `git checkout` on older Git).
- Never push directly to `main`. Always use a `codex/<task>` branch.

## Flow Overview
1. **Create a repository (if needed)**
   - Use GitHub MCP `create_repository` / `github__create_repository` and always set `private: true`:
     ```json
     {
       "name": "project-name",
       "description": "...",
       "private": true
     }
     ```
   - After creation, run `git remote add origin <repo-url>` locally. Public repos are not allowed.
2. **Sync main**
   ```bash
   git fetch origin
   git switch main   # use checkout on older Git
   git status        # ensure clean
   git pull --ff-only origin main
   ```
3. **Branch handling**
   - If an existing branch is not merged, continue with `git switch <branch>` and edit there.
   - If merged into main, create a new branch with `git switch -c codex/<task-name>` (e.g. `codex/git-ops-skill`). Use `git checkout -b ...` on older Git.
4. **Edit and sync**
   ```bash
   git add <files>
   git commit -m "type: summary"
   git fetch origin
   git rebase origin/main   # or git merge origin/main
   ```
5. **Push & PR**
   ```bash
   git push -u origin codex/<task>
   ```
   - Do not push to `main`. Create the PR via GitHub MCP `create_pull_request` and include purpose/changes/tests.
6. **After completion**
   ```bash
   git switch main
   git pull --ff-only origin main
   git branch -d codex/<task>
   ```

## Checklist
- [ ] Repository is private
- [ ] main is up to date at start
- [ ] Branch name follows `codex/<task>`
- [ ] Push is only from the working branch (`main` forbidden)
- [ ] PR link is shared in Slack

## Additional Notes
- If rebase is difficult, `git merge origin/main` is acceptable, but resolve conflicts locally before pushing.
- Use `git push --force-with-lease` only after rebase and with reviewer agreement.
