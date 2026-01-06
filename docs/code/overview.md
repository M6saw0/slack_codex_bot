# 全体像

## 目的
Slack の @メンションを起点に、Codex CLI をローカルで実行し、
同一スレッドへ進捗・結果を返す自動実行の流れを提供します。

## 構成
- `slack_bot/`:
  - Slack Socket Mode のアプリ本体。
  - `@codex-bot` メンションを受け取り、最近のスレッド履歴を付与して Codex CLI を起動。
- `codex_dir/`:
  - Codex CLI が実行される作業ディレクトリ。
  - 実際の開発対象リポジトリとして運用。

## 主要フロー
1. Slack で `@codex-bot` メンションを受信。
2. ボットが該当スレッドの履歴を取得し、ユーザー指示と合わせてプロンプトを構成。
3. `codex exec --full-auto` を `codex_dir/` で実行。
4. Codex は Slack MCP と GitHub MCP を使い、同一スレッドに進捗と結果を投稿。

## 主な設定値
- `SLACK_BOT_TOKEN`: Slack Bot Token
- `SLACK_APP_TOKEN`: Socket Mode 用 App Token
- `CODEX_ACTION_FOLDER`: Codex の実行ディレクトリ（`codex_dir/` の絶対パス）
- `SLACK_HISTORY_LIMIT`: 取得するスレッド履歴の件数

## 入口となるファイル
- `slack_bot/app-socket.py`
- `README.md`
