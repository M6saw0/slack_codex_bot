#!/usr/bin/env python3
import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone

WORK_LOGS_SCHEMA = """
CREATE TABLE IF NOT EXISTS work_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  query TEXT NOT NULL,
  action TEXT NOT NULL,
  detail TEXT,
  slack_thread TEXT,
  outputs TEXT,
  metadata JSON
);
CREATE INDEX IF NOT EXISTS idx_work_logs_ts ON work_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_work_logs_query ON work_logs(query);
"""


def default_db_path() -> str:
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    skills_dir = os.path.dirname(scripts_dir)
    codex_dir = os.path.dirname(os.path.dirname(skills_dir))
    base_dir = os.path.dirname(codex_dir)
    return os.path.join(base_dir, "work", "current", "work_logs.db")


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ensure_db(db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.executescript(WORK_LOGS_SCHEMA)


def insert_log(db_path: str, query: str, action: str, detail: str | None,
               slack_thread: str | None, outputs: str | None, metadata: dict | None,
               timestamp: str | None) -> None:
    ensure_db(db_path)
    payload = {
        "timestamp": timestamp or utc_now(),
        "query": query,
        "action": action,
        "detail": detail,
        "slack_thread": slack_thread,
        "outputs": outputs,
        "metadata": json.dumps(metadata) if metadata else None,
    }
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO work_logs (timestamp, query, action, detail, slack_thread, outputs, metadata)
            VALUES (:timestamp, :query, :action, :detail, :slack_thread, :outputs, :metadata)
            """,
            payload,
        )
        conn.commit()


def query_logs(db_path: str, query_like: str | None, action: str | None, limit: int) -> None:
    ensure_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        sql = "SELECT * FROM work_logs"
        params = []
        clauses = []
        if query_like:
            clauses.append("query LIKE ?")
            params.append(f"%{query_like}%")
        if action:
            clauses.append("action = ?")
            params.append(action)
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
    for row in rows:
        metadata = row["metadata"]
        try:
            metadata = json.loads(metadata) if metadata else None
        except json.JSONDecodeError:
            pass
        print({**dict(row), "metadata": metadata})


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage work folder logs (ensure/insert/query)")
    parser.add_argument("--db", default=default_db_path(), help="Path to work_logs.db")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ensure", help="Create DB and tables if missing")

    insert_cmd = sub.add_parser("insert", help="Insert log entry")
    insert_cmd.add_argument("--query", required=True)
    insert_cmd.add_argument("--action", required=True)
    insert_cmd.add_argument("--detail")
    insert_cmd.add_argument("--slack-thread")
    insert_cmd.add_argument("--outputs")
    insert_cmd.add_argument("--metadata", help="JSON string")
    insert_cmd.add_argument("--timestamp", help="ISO timestamp (optional)")

    query_cmd = sub.add_parser("query", help="Query log entries")
    query_cmd.add_argument("--query-like")
    query_cmd.add_argument("--action")
    query_cmd.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    if args.command == "ensure":
        ensure_db(args.db)
    elif args.command == "insert":
        metadata = json.loads(args.metadata) if args.metadata else None
        insert_log(
            args.db,
            args.query,
            args.action,
            args.detail,
            args.slack_thread,
            args.outputs,
            metadata,
            args.timestamp,
        )
    elif args.command == "query":
        query_logs(args.db, args.query_like, args.action, args.limit)


if __name__ == "__main__":
    main()
