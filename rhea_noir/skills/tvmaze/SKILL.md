---
name: tvmaze
description: Search TV shows/people and manage user dashboard via TVmaze API
---

# TVmaze Skill

Integrates with TVmaze API for rich TV metadata and user account management.

## Requirements
- `TVMAZE_API_KEY` environment variable.

## Features
- **Search**: Find shows/people by name.
- **My Shows**: List followed shows / episodes to watch (if key provided).
- **Metadata**: Get high-quality summary, image, cast, and episode release dates.

## Usage
```python
skill.execute("search", query="Doctor Who")
skill.execute("dashboard")
```
