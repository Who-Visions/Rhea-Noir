---
name: documents
version: 1.0.0
description: Gemini Document Processing - PDF analysis and extraction
---

# Documents Skill

Process PDFs with native vision - text, images, charts, tables.

## Features

- Analyze up to 1000 pages per PDF
- Extract structured data
- Summarize and Q&A
- Transcribe with formatting

## Usage

```python
from rhea_noir.skills.documents.actions import skill as docs

# Summarize a PDF
result = docs.summarize("path/to/document.pdf")

# Ask questions
result = docs.ask("path/to/document.pdf", "What are the key findings?")

# Extract structured data
result = docs.extract(
    "path/to/invoice.pdf",
    fields=["total", "date", "items"]
)

# Compare multiple PDFs
result = docs.compare(
    ["paper1.pdf", "paper2.pdf"],
    question="What are the differences?"
)
```

## Limits

- 50MB or 1000 pages per PDF
- 258 tokens per page
