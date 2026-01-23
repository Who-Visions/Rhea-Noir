---
name: skill-creator
description: Defines the standard for creating new Antigravity Skills. Use this meta-skill whenever you need to create, scaffold, or refine another skill.
---

# Skill Creator Skill

This skill governs the creation of other Antigravity Skills. It ensures consistency, best practices, and high-quality instruction sets.

## Core Principles
1.  **Atomic Purpose**: Each skill should do one thing exceptionally well.
2.  **Explicit Instructions**: Do not assume the agent knows specific project context.
3.  **Progressive Disclosure**: Push heavy logic into scripts or templates; keep `SKILL.md` for high-level direction.

## Directory Structure
Always follow this structure when creating a new skill:
```text
<skill-name>/
├── SKILL.md        (Required: The brain)
├── scripts/        (Optional: The hands - Python/Bash/Node)
├── references/     (Optional: The knowledge - Docs/Templates)
└── examples/       (Optional: The training - Inputs/Outputs)
```

## SKILL.md Template
Every `SKILL.md` must start with this YAML frontmatter:

```yaml
---
name: <skill-name-kebab-case>
description: <Trigger phrase>. Use this when <specific condition>.
---
```

### Sections to Include
-   **Goal**: What does this skill achieve?
-   **Instructions**: Step-by-step logic.
-   **Constraints**: What NOT to do (e.g., "Do not delete files").
-   **Example Usage**: A brief conversation snippet showing the user prompt and expected agent action.

## Best Practices
-   **Scripts**: Prefer Python for logic. Always provide a clear `usage` string in scripts.
-   **Dependencies**: If a script needs libraries, check if they are standard. If not, instruct the agent to install them or check availability.
-   **Validation**: When creating a skill, always instruct the agent to *test* it immediately after creation if possible.
