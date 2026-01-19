---
name: filesearch
version: 1.0.0
description: Gemini File Search (RAG) - semantic search over your documents
---

# File Search Skill (Gemini RAG)

Enable Retrieval Augmented Generation (RAG) using Gemini's File Search API. Upload documents, create knowledge stores, and query with semantic search.

## Features

- **Semantic Search**: Find relevant info by meaning, not just keywords
- **Auto Chunking**: Documents automatically split and indexed
- **Free Storage**: No cost for storage or query-time embeddings
- **Citations**: Responses include source references
- **Structured Output**: Get typed responses (Gemini 3+)

## Capabilities

| Action | Description |
|--------|-------------|
| `create_store` | Create a new file search store |
| `upload_file` | Upload and index a file |
| `query` | Query the store with semantic search |
| `list_stores` | List all file search stores |
| `list_documents` | List documents in a store |
| `delete_store` | Delete a store |
| `delete_document` | Delete a document from store |

## Supported File Types

- **Documents**: PDF, Word, Excel, PowerPoint
- **Code**: Python, JS, TS, Java, Go, Rust, etc.
- **Text**: Markdown, TXT, CSV, JSON, XML, YAML
- **Web**: HTML, CSS

## Usage Examples

### Create Store and Upload Files
```python
from rhea_noir.skills.filesearch.actions import skill as fs

# Create a knowledge store
store = fs.create_store("rhea-knowledge-base")

# Upload documents
fs.upload_file(store, "./docs/architecture.md")
fs.upload_file(store, "./docs/api-reference.pdf")
```

### Query with Semantic Search
```python
result = fs.query(
    store_name=store,
    question="How does the authentication system work?",
    model="gemini-3-flash-preview"
)
print(result["answer"])
print(result["citations"])
```

### Add Metadata for Filtering
```python
fs.upload_file(
    store,
    "./books/i-claudius.txt",
    metadata={"author": "Robert Graves", "year": 1934}
)

# Query with filter
result = fs.query(
    store_name=store,
    question="What happened to Claudius?",
    metadata_filter='author="Robert Graves"'
)
```

### Structured Output
```python
from pydantic import BaseModel

class Summary(BaseModel):
    title: str
    key_points: list[str]
    
result = fs.query_structured(
    store_name=store,
    question="Summarize the main architecture",
    response_schema=Summary
)
```

## Pricing

- **Indexing**: $0.15 per 1M tokens (one-time)
- **Storage**: FREE
- **Query embeddings**: FREE  
- **Retrieved tokens**: Normal Gemini pricing

## Limits

| Tier | Max Store Size |
|------|----------------|
| Free | 1 GB |
| Tier 1 | 10 GB |
| Tier 2 | 100 GB |
| Tier 3 | 1 TB |

> [!NOTE]
> Keep stores under 20 GB for optimal retrieval latency.
