---
name: work-summary-updater
description: >-
  Update work_index/index.json and index.json based on recent work folder activity and
  work_index.db. Use at the end of a task.
---

# Work Summary Updater Skill

このスキルは、作業開始時のルーティング判断と、作業完了時の **index.json（唯一の正）** 更新を行う手順です。

## 対象
- `work_index/index.json`（唯一の正）
- `work_index/work_index.db`

## 付属スクリプト
- `scripts/manage_work_index.py` : work_index 用の ensure/upsert/query

## ルーティング手順
1. 指示文を要約し、主要キーワードを抽出する。
2. `index.json` の `keywords` / `query_patterns` を照合する。
3. 一致度が高い作業フォルダを選択する。
4. 候補が複数・曖昧な場合は Slack で確認する。
5. 該当が無い場合は `work/<短い名前>` を新規作成する。

## 更新方針
- `index.json` は最新のユーザー要求やリポジトリ状況を反映する。

## 更新手順
1. `work_index/work_index.db` の最新レコードを参照する。
2. 更新対象フォルダの `summary` / `tags` / `query_patterns` を整理する。
3. `index.json` を更新する（唯一の正・最新の要求/状況を反映）。

## 書式ルール
- `index.json` は `folder` / `summary` / `keywords` / `query_patterns` / `last_used` を含める

## 注意
- `index.json` が唯一の正とする。
- JSONは有効な形式を保つ（末尾カンマ禁止）。

## 使い方例
```bash
python scripts/manage_work_index.py ensure
python scripts/manage_work_index.py query --limit 5
```
