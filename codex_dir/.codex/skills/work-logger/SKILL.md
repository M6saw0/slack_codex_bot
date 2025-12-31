---
name: work-logger
description: >-
  Record per-task work logs into each work folder's SQLite DB and update the global
  work_index.db summary after meaningful steps. Use whenever work starts or finishes.
---

# Work Logger Skill

このスキルは、作業内容を **各作業フォルダの SQLite** と **親フォルダの集約DB** に記録・参照するための手順です。

## 付属スクリプト
- `scripts/manage_work_logs.py` : work_logs 用の ensure/insert/query

## 対象DB
- 作業フォルダ側: `work/<project>/work_logs.db`（無ければ自動作成）
- 親フォルダ側: `work_index/work_index.db`（無ければ自動作成）

## 記録タイミング
- 作業開始時（クエリ受領・フォルダ決定）
- 主要変更完了時
- テスト実施時
- 作業完了時（返信要約込み）

## 記録内容（作業フォルダDB）
- `query`: ユーザー指示の要約
- `action`: `start` / `update` / `test` / `finish`
- `detail`: 実施内容
- `slack_thread`: `channel_id:thread_ts`
- `outputs`: PR や成果物の要約
- `metadata`: 追加情報（JSON）

## 実装上の推奨
- ログ登録・参照は上記スクリプトを使い、DBが無い場合は自動作成する。
- `sandbox/test-sqlite-skills/scripts/manage_logs.py` を流用する。
- スキーマが異なる場合は `schema.sql` を拡張して整合させる。

## 使い方例
### 作業ログの作成/追記
```bash
python scripts/manage_work_logs.py ensure
python scripts/manage_work_logs.py insert \
  --query "ログイン画面の修正" \
  --action update \
  --detail "Login.tsx のバリデーションを調整" \
  --slack-thread "CXXXX:123456.789" \
  --outputs "PR #12" \
  --metadata '{"branch":"codex/login-fix"}'
```


## 注意
- 機密情報は DB に保存しない。
- Slack 会話は全文ではなく **要約** を保存する。
