# バックエンド

## 主要コンポーネント
- `slack_bot/app-socket.py`
  - Slack Socket Mode でメンションを受ける Python アプリ。
  - スレッド履歴を取得し、Codex CLI のプロンプトを構築。
  - `subprocess.Popen` で Codex CLI を非同期起動。
- `codex_dir/`
  - Codex CLI が実行される作業ディレクトリ。
  - 実際のコード修正・テスト・PR 作成が行われる場所。

## 処理フロー（詳細）
1. `app_mention` イベント受信。
2. 直近のスレッド履歴を `conversations_replies` で取得。
3. ユーザーの指示文と履歴 JSON を組み合わせてプロンプトを生成。
4. `codex exec --full-auto --skip-git-repo-check` を `CODEX_ACTION_FOLDER` で起動。

## 主要な関数
- `_history_limit()`
  - `SLACK_HISTORY_LIMIT` から取得件数を安全に決定。
- `_fetch_recent_history()`
  - スレッドもしくはチャンネルの履歴を取得し、簡易 JSON に整形。
- `handle_app_mention()`
  - メンションの受理、履歴取得、プロンプト生成、Codex 起動を担当。

## 依存関係
- `slack-bolt`
- `python-dotenv`

## 設定ファイル
- `slack_bot/.env` に Slack トークンや `CODEX_ACTION_FOLDER` を指定。
