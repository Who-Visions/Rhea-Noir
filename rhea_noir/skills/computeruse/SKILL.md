---
name: computeruse
version: 1.0.0
description: Gemini Computer Use - Browser automation with AI vision
---

# Computer Use Skill (Gemini Browser Automation)

Enable Rhea to **see and control** a browser using Gemini 2.5 Computer Use model. The AI analyzes screenshots and generates mouse/keyboard actions.

## Features

- **Visual Understanding**: AI sees the screen via screenshots
- **Browser Control**: Click, type, scroll, navigate
- **Multi-step Tasks**: Chains actions to complete complex goals
- **Safety Checks**: Built-in confirmation for risky actions

## Capabilities

| Action | Description |
|--------|-------------|
| `run_task` | Execute a multi-step browser task |
| `click_at` | Click at coordinates |
| `type_text_at` | Type text at coordinates |
| `navigate` | Go to a URL |
| `scroll` | Scroll the page |
| `take_screenshot` | Capture current state |

## Requirements

```bash
pip install google-genai playwright
playwright install chromium
```

## Usage Examples

### Run a Web Research Task
```python
from rhea_noir.skills.computeruse.actions import skill as cu

result = cu.run_task(
    goal="Search for 'best AI frameworks 2026' on Google and list the top 3 results",
    start_url="https://www.google.com",
    max_steps=10
)
print(result["final_answer"])
```

### Automate Form Filling
```python
result = cu.run_task(
    goal="Fill out the contact form with name 'Dave', email 'dave@example.com', and submit",
    start_url="https://example.com/contact"
)
```

### Web Scraping with Context
```python
result = cu.run_task(
    goal="Go to Amazon and find the price of Sony WH-1000XM5 headphones",
    start_url="https://www.amazon.com"
)
```

## Safety Features

The model includes built-in safety checks:
- **require_confirmation**: User must approve risky actions
- **Excluded actions**: Block specific UI actions if needed

```python
result = cu.run_task(
    goal="...",
    excluded_actions=["drag_and_drop"],
    require_human_confirmation=True
)
```

## Supported UI Actions

| Action | Description |
|--------|-------------|
| `open_web_browser` | Open browser |
| `navigate` | Go to URL |
| `click_at` | Click at (x, y) |
| `type_text_at` | Type text at (x, y) |
| `scroll_document` | Scroll up/down/left/right |
| `scroll_at` | Scroll at specific location |
| `hover_at` | Hover mouse at (x, y) |
| `key_combination` | Press keys (e.g., "Control+C") |
| `go_back` | Browser back |
| `go_forward` | Browser forward |
| `wait_5_seconds` | Wait for page load |
| `drag_and_drop` | Drag element |

## Model

Uses `gemini-2.5-computer-use-preview-10-2025` - specialized for browser control.

> [!CAUTION]
> Computer Use is a Preview feature. Supervise closely for important tasks.
