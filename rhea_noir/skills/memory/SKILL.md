# Memory Skill

Store, recall, and sync conversation memories.

## Description

Rhea's memory system provides persistent storage for conversations and learned content. Uses SQLite for fast local access and BigQuery for cloud persistence.

## Actions

- `store` — Store a message in memory with optional keywords
- `recall` — Search memories by query
- `sync` — Force sync local memories to cloud
- `stats` — Get memory statistics

## Usage

```python
# Store a memory
skill.execute("store", role="user", content="I love anime!", keywords=["anime", "hobby"])

# Recall memories
skill.execute("recall", query="anime", limit=5)

# Get stats
skill.execute("stats")

# Force cloud sync
skill.execute("sync")
```

## Resources

- Local: `~/.rhea_noir/memory.db` (SQLite)
- Cloud: BigQuery `rhea-noir.memories.conversations`
