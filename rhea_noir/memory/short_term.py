"""
Short-Term Memory - SQLite-based local storage for fast access
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class ShortTermMemory:
    """SQLite-based local memory for fast, instant access"""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize SQLite database for short-term memory"""
        if db_path is None:
            # Default to user's home directory
            db_dir = Path.home() / ".rhea_noir"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "memory.db")

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    keywords TEXT,
                    metadata TEXT,
                    session_id TEXT,
                    synced INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS keywords (
                    keyword TEXT PRIMARY KEY,
                    frequency INTEGER DEFAULT 1,
                    importance REAL DEFAULT 1.0,
                    related TEXT,
                    last_used TEXT,
                    category TEXT
                )
            """)
            # Identity and expressions table for Rhea's core data
            conn.execute("""
                CREATE TABLE IF NOT EXISTS identity (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    category TEXT,
                    updated_at TEXT
                )
            """)
            # Create indexes for fast search
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_role ON memories(role)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_synced ON memories(synced)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_identity_category ON identity(category)")
            conn.commit()

    def store(
        self,
        role: str,
        content: str,
        keywords: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Store a memory entry, returns the memory ID"""
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO memories (id, timestamp, role, content, keywords, metadata, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory_id,
                    timestamp,
                    role,
                    content,
                    json.dumps(keywords or []),
                    json.dumps(metadata or {}),
                    session_id
                )
            )
            conn.commit()

        return memory_id

    def recall(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories by content (simple text search)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM memories
                WHERE content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (f"%{query}%", limit)
            )
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "role": row["role"],
                    "content": row["content"],
                    "keywords": json.loads(row["keywords"]) if row["keywords"] else [],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                    "session_id": row["session_id"]
                })
            return results

    def get_context(self, n_messages: int = 20) -> List[Dict[str, Any]]:
        """Get the last N messages for context"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM memories
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (n_messages,)
            )
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "role": row["role"],
                    "content": row["content"],
                    "keywords": json.loads(row["keywords"]) if row["keywords"] else [],
                })
            # Return in chronological order
            return list(reversed(results))

    def get_unsynced(self) -> List[Dict[str, Any]]:
        """Get memories that haven't been synced to cloud"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM memories WHERE synced = 0 ORDER BY timestamp"
            )
            return [dict(row) for row in cursor.fetchall()]

    def mark_synced(self, memory_ids: List[str]):
        """Mark memories as synced to cloud"""
        with sqlite3.connect(self.db_path) as conn:
            placeholders = ",".join("?" * len(memory_ids))
            conn.execute(
                f"UPDATE memories SET synced = 1 WHERE id IN ({placeholders})",
                memory_ids
            )
            conn.commit()

    def get_stats(self) -> Dict[str, int]:
        """Get memory statistics"""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            synced = conn.execute("SELECT COUNT(*) FROM memories WHERE synced = 1").fetchone()[0]
            keywords = conn.execute("SELECT COUNT(*) FROM keywords").fetchone()[0]
            identity = conn.execute("SELECT COUNT(*) FROM identity").fetchone()[0]
            return {
                "total_memories": total,
                "synced": synced,
                "unsynced": total - synced,
                "keywords": keywords,
                "identity_items": identity
            }

    def clear(self):
        """Clear all local memories (for testing)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memories")
            conn.execute("DELETE FROM keywords")
            conn.commit()

    def store_identity(self, key: str, value: Any, category: str = "general") -> None:
        """Store an identity/expression value"""
        timestamp = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO identity (key, value, category, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (key, json.dumps(value), category, timestamp)
            )
            conn.commit()

    def get_identity(self, key: str) -> Optional[Any]:
        """Retrieve an identity/expression value"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM identity WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    def get_identity_by_category(self, category: str) -> Dict[str, Any]:
        """Get all identity values in a category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT key, value FROM identity WHERE category = ?",
                (category,)
            )
            return {row[0]: json.loads(row[1]) for row in cursor.fetchall()}

    def seed_expressions(self, expressions_data: Dict[str, Any]) -> int:
        """
        Seed the identity table with expressions/emoji data.
        Returns count of items seeded.
        """
        count = 0
        timestamp = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Store identity info
            if "identity" in expressions_data:
                for key, value in expressions_data["identity"].items():
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO identity (key, value, category, updated_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (f"identity_{key}", json.dumps(value), "identity", timestamp)
                    )
                    count += 1

            # Store expression categories
            if "expressions" in expressions_data:
                for category, data in expressions_data["expressions"].items():
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO identity (key, value, category, updated_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (f"expr_{category}", json.dumps(data), "expressions", timestamp)
                    )
                    count += 1

            conn.commit()

        return count

    def is_expressions_seeded(self) -> bool:
        """Check if expressions have been seeded"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM identity WHERE category = 'expressions'"
            )
            return cursor.fetchone()[0] > 0

