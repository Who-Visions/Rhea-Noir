---
name: brand-design
description: Applies consistent brand identity, design tokens, and copywriting voice to projects. Use when designing UI, writing content, or setting up frontend themes.
---

# Brand Design Skill

This skill ensures that all generated designs and content adhere to the organization's brand guidelines.

## Instructions

1.  **Load Guidelines**:
    -   Read `resources/brand_identity.md` for visual design tokens (colors, fonts, spacing).
    -   Read `resources/copywriting.md` for tone of voice and content rules.

2.  **Apply to UI Tasks**:
    -   When generating CSS/Tailwind configs, use the exact hex codes from the identity file.
    -   When designing components, strictly follow the border radius and shadow specifications.

3.  **Apply to Content Tasks**:
    -   When writing landing page copy or emails, cross-reference the Tone of Voice guidelines.
    -   Ensure forbidden words are avoided.

## Resources
-   **Identity**: `resources/brand_identity.md`
-   **Copy**: `resources/copywriting.md`

## Example Usage
**User**: "Create a landing page hero section."
**Agent**: 
1. Reads `brand_identity.md` -> Sets primary color #FF5733, Font Inter.
2. Reads `copywriting.md` -> Writes headline in "Confident" tone.
3. Generates code matching these constraints.
