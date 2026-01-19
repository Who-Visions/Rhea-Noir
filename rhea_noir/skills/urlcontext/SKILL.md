---
name: urlcontext
version: 1.0.0
description: Gemini URL Context - Analyze and compare web pages
---

# URL Context Skill

Provide URLs as context to Gemini for analysis, comparison, and synthesis.

## Features

- **Extract Data**: Pull prices, names, key findings from URLs
- **Compare Documents**: Analyze multiple pages side-by-side
- **Synthesize Content**: Combine info from sources into reports
- **Code Analysis**: Point to GitHub repos or docs for explanation

## Capabilities

| Action | Description |
|--------|-------------|
| `analyze_url` | Analyze content from a single URL |
| `compare_urls` | Compare content from multiple URLs |
| `synthesize` | Create content from multiple sources |
| `extract_data` | Pull specific data from URLs |

## Usage Examples

### Analyze a Page
```python
from rhea_noir.skills.urlcontext.actions import skill as uc

result = uc.analyze_url(
    url="https://example.com/article",
    question="What are the main points?"
)
```

### Compare Two Recipes
```python
result = uc.compare_urls(
    urls=[
        "https://site1.com/recipe",
        "https://site2.com/recipe"
    ],
    question="Compare ingredients and cooking times"
)
```

### Combine with Google Search
```python
result = uc.synthesize(
    urls=["https://example.com/doc"],
    question="Summarize and add recent updates",
    use_google_search=True
)
```

## Supported Content

- **Text**: HTML, JSON, plain text, XML, CSS, JS, CSV
- **Images**: PNG, JPEG, BMP, WebP
- **PDFs**: application/pdf

## Limits

- Max 20 URLs per request
- Max 34MB per URL
- No paywalled content, YouTube, or Google Workspace files
