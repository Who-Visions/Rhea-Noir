# Ingest Skill

High-fidelity knowledge ingestion for Rhea Noir. 

## Capability
The Ingest skill centralizes all intelligence gathering from external sources (YouTube, PDFs, Markdown, Web URLs) and parses them into the VeilVerse Notion DB and local LoreDB.

## Actions

### `ingest`
Analyzes content and pushes structured entities to Rhea's memory.
- **url**: (Optional) YouTube URL or Web URL.
- **content**: (Optional) Raw text or transcript.
- **hint**: (Optional) Custom focus for the LLM analysis (e.g., "Focus on electrical infrastructure").
- **dry_run**: (Optional) Preview analysis without saving.

### `verify`
Checks if a specific concept or URL has already been ingested into memory.
- **query**: Search term or URL.

## Example
```bash
rhea execute ingest ingest url="https://youtube.com/watch?v=..." hint="Massive chemical reactor"
```
