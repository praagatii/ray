import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path


class LongTermMemory:
    def __init__(self, db_path: str = None):
        if db_path is None:
            base = Path(__file__).parent.parent / "data"
            base.mkdir(exist_ok=True)
            db_path = str(base / "memory.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    source TEXT DEFAULT 'unknown',
                    metadata TEXT DEFAULT '{}',
                    embedding TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_source ON memories(source)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")

    def store(self, content: str, source: str = "conversation", metadata: dict = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO memories (content, source, metadata) VALUES (?, ?, ?)",
                (content, source, json.dumps(metadata or {}))
            )

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, content, source, metadata, created_at FROM memories WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?",
                (f"%{query}%", top_k)
            ).fetchall()
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "content": row[1],
                "source": row[2],
                "metadata": json.loads(row[3]),
                "timestamp": row[4],
                "score": 1.0
            })
        return results

    def get_recent(self, limit: int = 20) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, content, source, metadata, created_at FROM memories ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [{
            "id": r[0], "content": r[1], "source": r[2],
            "metadata": json.loads(r[3]), "timestamp": r[4]
        } for r in rows]

    def clear(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memories")

    def get_stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            sources = conn.execute("SELECT source, COUNT(*) as cnt FROM memories GROUP BY source ORDER BY cnt DESC").fetchall()
        return {"total_memories": count, "sources": dict(sources)}
