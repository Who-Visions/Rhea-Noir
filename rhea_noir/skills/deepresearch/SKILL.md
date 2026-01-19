---
name: deepresearch
version: 1.0.0
description: Gemini Deep Research Agent - Multi-step research tasks
---

# Deep Research Skill

Autonomous research agent that plans, searches, and synthesizes detailed reports.

## Features

- **Multi-step Research**: Plans and executes complex research
- **Web + Your Data**: Uses Google Search + File Search
- **Cited Reports**: Sources for every claim
- **Streaming**: Real-time progress updates

## Usage

```python
from rhea_noir.skills.deepresearch.actions import skill as dr

# Start research (async, can take minutes)
result = dr.research(
    query="Compare the top 5 AI frameworks in 2026",
    format_instructions="Include comparison table"
)
print(result["report"])
print(result["sources"])
```

### With Your Data (File Search)
```python
result = dr.research_with_files(
    query="Compare our Q4 report against industry trends",
    file_store="fileSearchStores/my-store"
)
```

## Pricing

~$2-5 per research task depending on complexity.

> [!NOTE]
> Uses Interactions API. Tasks can take 1-20 minutes.
