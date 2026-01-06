# フロントエンド

## 位置づけ
このリポジトリには独自の Web フロントエンドはありません。
ユーザーとの UI は **Slack クライアント**（アプリ/ブラウザ）で完結します。

## ユーザー体験（UI）
- Slack チャンネルで `@codex-bot` をメンション。
- そのスレッド内で進捗・結果が返信される。
- 追加の指示も同スレッドで継続可能。

## 設定上のポイント
- Slack App を Socket Mode で構成。
- `app_mention` のイベント購読が必要。
- Bot Scopes は `app_mentions:read` / `chat:write` / `groups:history` を利用。

## 実体のコード
フロントエンドの UI コードは持たず、Slack の既存 UI を利用します。
