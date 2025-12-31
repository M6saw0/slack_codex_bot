#!/usr/bin/env python3
import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone

WORK_INDEX_SCHEMA = """
CREATE TABLE IF NOT EXISTS work_index (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  folder TEXT NOT NULL UNIQUE,
  summary TEXT NOT NULL,
  tags TEXT,
  query_patterns TEXT,
  last_used TEXT,
  metadata JSON
);
CREATE INDEX IF NOT EXISTS idx_work_index_folder ON work_index(folder);
CREATE INDEX IF NOT EXISTS idx_work_index_last_used ON work_index(last_used);
"""


def default_db_path() -> str:
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    skills_dir = os.path.dirname(scripts_dir)
    codex_dir = os.path.dirname(os.path.dirname(skills_dir))
    base_dir = os.path.dirname(codex_dir)
    return os.path.join(base_dir, "work_index", "work_index.db")


def utc_today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def ensure_db(db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.executescript(WORK_INDEX_SCHEMA)


def upsert_entry(db_path: str, folder: str, summary: str, tags: str | None,
                 query_patterns: str | None, last_used: str | None, metadata: dict | None) -> None:
    ensure_db(db_path)
    payload = {
        "folder": folder,
        "summary": summary,
        "tags": tags,
        "query_patterns": query_patterns,
        "last_used": last_used or utc_today(),
        "metadata": json.dumps(metadata) if metadata else None,
    }
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO work_index (folder, summary, tags, query_patterns, last_used, metadata)
            VALUES (:folder, :summary, :tags, :query_patterns, :last_used, :metadata)
            ON CONFLICT(folder) DO UPDATE SET
              summary=excluded.summary,
              tags=excluded.tags,
              query_patterns=excluded.query_patterns,
              last_used=excluded.last_used,
              metadata=excluded.metadata
            """,
            payload,
        )
        conn.commit()


def query_entries(db_path: str, folder_like: str | None, limit: int) -> None:
    ensure_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        sql = "SELECT * FROM work_index"
        params = []
        if folder_like:
            sql += " WHERE folder LIKE ?"
            params.append(f"%{folder_like}%")
        sql += " ORDER BY last_used DESC LIMIT ?"
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
    parser = argparse.ArgumentParser(description="Manage routing index (ensure/upsert/query)")
    parser.add_argument("--db", default=default_db_path(), help="Path to work_index.db")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ensure", help="Create DB and tables if missing")

    upsert_cmd = sub.add_parser("upsert", help="Insert or update routing entry")
    upsert_cmd.add_argument("--folder", required=True)
    upsert_cmd.add_argument("--summary", required=True)
    upsert_cmd.add_argument("--tags")
    upsert_cmd.add_argument("--query-patterns")
    upsert_cmd.add_argument("--last-used")
    upsert_cmd.add_argument("--metadata", help="JSON string")

    query_cmd = sub.add_parser("query", help="Query routing entries")
    query_cmd.add_argument("--folder-like")
    query_cmd.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    if args.command == "ensure":
        ensure_db(args.db)
    elif args.command == "upsert":
        metadata = json.loads(args.metadata) if args.metadata else None
        upsert_entry(
            args.db,
            args.folder,
            args.summary,
            args.tags,
            args.query_patterns,
            args.last_used,
            metadata,
        )
    elif args.command == "query":
        query_entries(args.db, args.folder_like, args.limit)


if __name__ == "__main__":
    main()
