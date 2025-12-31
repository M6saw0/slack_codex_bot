---
name: git-operations
description: >-
  Workflow for using GitHub MCP + git to create private repos, sync main via git switch,
  branch safely, push without touching main, and open PRs. Use for any task that needs
  Git branching/publishing guidance.
---

# Git Operations Skill

Useこのスキルで GitHub MCP とローカル `git` の運用を統一します。ここに必要な手順をすべて記載します。

## 前提
- GitHub MCP で `create_repository` を呼び出せる（PAT 設定済み）。
- ローカルに `git switch` が利用可能（古い Git では `git checkout` を使う）。
- main へ直接 push は禁止。常に `codex/<task>` 形式のブランチを使う。

## フロー概要
1. **リポジトリ作成（必要な場合）**
   - GitHub MCP の `create_repository` / `github__create_repository` を使い、必ず `private: true` を指定:
     ```json
     {
       "name": "project-name",
       "description": "...",
       "private": true
     }
     ```
   - 作成後にローカルで `git remote add origin <repo-url>` を実行。パブリックリポは禁止。
2. **main の同期**
   ```bash
   git fetch origin
   git switch main   # 旧 Git は checkout
   git status        # クリーン確認
   git pull --ff-only origin main
   ```
3. **ブランチ扱い**
   - 既存ブランチが未マージなら `git switch <branch>` で継続し、そのブランチ上で修正。
   - main にマージ済みであれば `git switch -c codex/<task-name>`（例 `codex/git-ops-skill`）で新規ブランチを作成。旧 Git では `git checkout -b ...`。
4. **編集と同期**
   ```bash
   git add <files>
   git commit -m "type: summary"
   git fetch origin
   git rebase origin/main   # or git merge origin/main
   ```
5. **push & PR**
   ```bash
   git push -u origin codex/<task>
   ```
   - `main` へ push しない。GitHub MCP `create_pull_request` で PR を作成し、目的/変更/テストを記載。
6. **完了後**
   ```bash
   git switch main
   git pull --ff-only origin main
   git branch -d codex/<task>
   ```

## チェックリスト
- [ ] リポジトリは必ずプライベート
- [ ] 作業開始時に main を最新化
- [ ] ブランチ名は `codex/<task>` で一意化
- [ ] push は常に作業ブランチ（`main` 禁止）
- [ ] PR 作成後に Slack へリンクを共有

## 追加メモ
- rebase が苦手な場合は `git merge origin/main` でも構いませんが、コンフリクトはローカルで解決してから push。
- `git push --force-with-lease` は rebase 後の履歴修正時のみ、レビュワーと合意して実施。
