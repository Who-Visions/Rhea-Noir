# Search Skill

Search across knowledge bases, web, and memory.

## Actions

- `web` — Search the web using Google Search grounding
- `knowledge` — Search Vertex AI knowledge base
- `memory` — Search local memories
- `unified` — Search all sources

## Usage

```python
skill.execute("web", query="what is MCP in AI?")
skill.execute("memory", query="anime recommendations")
skill.execute("unified", query="cosplay tips", sources=["web", "memory"])
```
