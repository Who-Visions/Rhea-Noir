---
name: planning
description: Creates comprehensive implementation plans for complex tasks. Use when the user asks to "plan", "architect", or "roadmap" a feature or project.
---

# Planning Skill

This skill forces a deliberate planning phase before execution, ensuring high-quality, thought-out solutions.

## Goal
To produce a detailed, step-by-step implementation plan that anticipates edge cases and structural requirements.

## Instructions
1.  **Clarify Goals**: Restate the user's objective to ensure alignment.
2.  **Architecture/Design**:
    -   Outline core components/classes.
    -   Define data structures or database innovations.
    -   Identify necessary dependencies or tools.
3.  **Step-by-Step Plan**:
    -   Break the work into small, atomic tasks.
    -   Order tasks logically (dependencies first).
    -   Mark valid verification steps for each task.
4.  **Risk Assessment**: Identify potential bottlenecks or "unknowns" that need research.

## Format
Use Markdown headers and checkboxes for the plan.

```markdown
# Implementation Plan: [Title]

## design
...

## Tasks
- [ ] Task 1: [Description]
- [ ] Task 2: [Description]

## Verification
- [ ] How to test Task 1
- [ ] How to test Task 2
```

## Constraints
-   Do not write code in the plan unless it's pseudo-code or small snippets for clarity.
-   Focus on *strategy* over *syntax*.
