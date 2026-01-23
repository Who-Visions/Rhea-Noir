import aiosqlite
import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

class LoreMemoryService:
    """
    Local SQLite persistence for Rhea's Lore Memory.
    Provides fast, asynchronous lookups of mirrored Notion data.
    """
    
    DB_PATH = "veillore.db"

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    async def initialize(self):
        """Initializes the SQLite database and creates tables if they don't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    notion_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT,
                    description TEXT,
                    content TEXT,
                    era TEXT,
                    last_edited DATETIME,
                    url TEXT,
                    last_synced DATETIME,
                    score REAL DEFAULT 0
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    source_id TEXT,
                    target_id TEXT,
                    rel_type TEXT,
                    PRIMARY KEY (source_id, target_id, rel_type),
                    FOREIGN KEY (source_id) REFERENCES entities(notion_id),
                    FOREIGN KEY (target_id) REFERENCES entities(notion_id)
                )
            """)
            
            # Migration: Add score column if it doesn't exist
            try:
                await db.execute("ALTER TABLE entities ADD COLUMN score REAL DEFAULT 0")
            except Exception:
                pass  # Column likely exists

            await db.execute("""
                CREATE TABLE IF NOT EXISTS hindsight_notes (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME,
                    task_name TEXT,
                    trigger_event TEXT,
                    outcome TEXT,
                    key_lesson TEXT,
                    content_json TEXT
                )
            """)
            await db.commit()
            print(f"🧠 LoreMemory: Database initialized at {self.db_path}")

    async def upsert_entity(self, entity_data: Dict[str, Any]):
        """Inserts or updates a lore entity."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO entities (
                    notion_id, name, category, description, content, era, last_edited, url, last_synced, score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(notion_id) DO UPDATE SET
                    name=excluded.name,
                    category=excluded.category,
                    description=excluded.description,
                    content=excluded.content,
                    era=excluded.era,
                    last_edited=excluded.last_edited,
                    url=excluded.url,
                    last_synced=excluded.last_synced,
                    score=excluded.score
            """, (
                entity_data['notion_id'],
                entity_data['name'],
                entity_data['category'],
                entity_data['description'],
                entity_data.get('content', ''),
                entity_data.get('era', 'Unknown'),
                entity_data['last_edited'],
                entity_data['url'],
                datetime.now().isoformat(),
                entity_data.get('score', 0)
            ))
            await db.commit()

    async def search_lore(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Performs a text search across names, descriptions, and content."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            # Basic LIKE search for now, could upgrade to FTS5 later
            sql = """
                SELECT * FROM entities 
                WHERE name LIKE ? OR description LIKE ? OR content LIKE ?
                ORDER BY score DESC, last_edited DESC
                LIMIT ?
            """
            search_param = f"%{query}%"
            async with db.execute(sql, (search_param, search_param, search_param, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_entity(self, notion_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single entity by its Notion ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM entities WHERE notion_id = ?", (notion_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def add_hindsight_note(self, note: Dict[str, Any]):
        """Stores a hindsight note."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO hindsight_notes (
                    id, timestamp, task_name, trigger_event, outcome, key_lesson, content_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                note["id"],
                note["timestamp"],
                note["task_name"],
                note["trigger_event"],
                note["outcome"],
                note["key_lesson"],
                json.dumps(note)
            ))
            await db.commit()

    async def search_notes(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches hindsight notes."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            sql = """
                SELECT * FROM hindsight_notes 
                WHERE key_lesson LIKE ? OR task_name LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            search_param = f"%{query}%"
            async with db.execute(sql, (search_param, search_param, limit)) as cursor:
                rows = await cursor.fetchall()
                results = []
                for row in rows:
                    data = dict(row)
                    if data.get("content_json"):
                        try:
                            data.update(json.loads(data["content_json"]))
                        except:
                            pass
                    results.append(data)
                return results

    async def get_stats(self) -> Dict[str, Any]:
        """Returns database statistics."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM entities") as cursor:
                count = (await cursor.fetchone())[0]
            async with db.execute("SELECT MAX(last_edited) FROM entities") as cursor:
                last_update = (await cursor.fetchone())[0]
            return {
                "total_entities": count,
                "last_notion_edit": last_update
            }
