---
name: googlesearch
version: 1.0.0
description: Gemini Grounding with Google Search - Real-time web data
---

# Google Search Skill

Ground Gemini responses with real-time web search.

## Features

- **Reduce Hallucinations**: Ground answers in real data
- **Real-Time Info**: Access current events and news
- **Citations**: Verifiable sources for claims

## Usage

```python
from rhea_noir.skills.googlesearch.actions import skill as gs

result = gs.search(
    query="Who won the 2024 Super Bowl?",
    model="gemini-3-flash-preview"
)
print(result["answer"])
print(result["sources"])
```

## With URL Context

```python
result = gs.search_with_urls(
    query="Summarize this article and add recent updates",
    urls=["https://example.com/article"],
    model="gemini-3-flash-preview"
)
```
