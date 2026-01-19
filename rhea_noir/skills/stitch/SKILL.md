---
name: stitch
description: AI-powered UI and image generation using Gemini 3 (Nano Banana Pro)
---

# Stitch Skill

Generate production-ready UIs, components, and images using Google's Gemini 3 AI.

## Configuration
Requires `GEMINI_API_KEY` in environment variables.

## Models Used
- **gemini-3-pro-preview**: Code/UI generation with advanced reasoning
- **gemini-3-pro-image-preview**: Pro image generation (Nano Banana Pro) - up to 4K
- **gemini-2.5-flash-image**: Fast image generation (Nano Banana)

## Actions

### UI/Code Generation

#### `generate_ui`
Generate a complete UI from a text description.
- `prompt` (str): Description of the UI
- `format` (str): "html", "react", or "css"

#### `generate_component`
Generate a reusable UI component.
- `prompt` (str): Component description
- `framework` (str): "react", "vue", "svelte", or "html"

### Image Generation

#### `generate_image`
Generate an image from text.
- `prompt` (str): Image description
- `aspect_ratio` (str): "1:1", "16:9", "9:16", etc.
- `resolution` (str): "1K", "2K", or "4K"
- `output_path` (str): Path to save the image

#### `edit_image`
Edit an existing image.
- `prompt` (str): Edit instructions
- `image_path` (str): Path to source image
- `output_path` (str): Path to save edited image

#### `generate_logo`
Generate a professional logo.
- `prompt` (str): Logo description
- `output_path` (str): Path to save

#### `generate_infographic`
Generate an infographic with Google Search grounding.
- `prompt` (str): Infographic topic
- `output_path` (str): Path to save

## Examples

```python
# Generate UI code
result = skill.execute("generate_ui", prompt="a modern dashboard with sidebar", format="react")

# Generate an image
result = skill.execute("generate_image", 
    prompt="futuristic city at sunset", 
    aspect_ratio="16:9", 
    resolution="2K",
    output_path="city.png")

# Generate a logo
result = skill.execute("generate_logo",
    prompt="coffee shop called 'The Daily Grind'",
    output_path="logo.png")
```
