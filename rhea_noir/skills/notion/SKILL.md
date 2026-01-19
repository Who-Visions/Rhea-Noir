---
name: notion
description: Manage Notion pages and databases
---

# Notion Skill

Allows Rhea Noir to interact with the Notion API.

## Requirements
- `NOTION_TOKEN` environment variable must be set.
- Integration must be shared with specific pages/databases in Notion.

## Features
- **Identify**: Check bot identity.
- **Search**: List accessible pages and databases.
- **Read**: Read block children or page properties (basic).

## Usage

```python
skill.execute("me")
skill.execute("search", query="Project")
```
