---
name: hq-protocol
description: Enforces the Universal Operational Rules defined in the HQ Agent Registry (AGENTS.md).
keywords: [rules, protocol, standards, hq, agents]
priority: 100
light_feedback:
  neutral: deep_green
---
# HQ Operational Protocol

## Directive

This skill enforces strict adherence to the **Universal Operational Rules** defined in `C:\Users\super\Watchtower\HQ_WhoArt\AGENTS.md`.

## Critical Instructions

For EVERY task, you must:

1. **LOAD RULES**: Read Section 5 of `C:\Users\super\Watchtower\HQ_WhoArt\AGENTS.md` before writing any code.
2. **STACK ENFORCEMENT**:
    * **Frontend**: Next.js 16, React 19.2 (Turbopack enabled).
    * **Logic**: Strict TypeScript, Functional patterns.
    * **Style**: Tailwind CSS, Shadcn UI.
3. **PROHIBITED**:
    * No Semicolons (unless required).
    * No "guessing" frameworks (Must match AGENTS.md).
    * No legacy patterns (e.g., Pages router for Next.js).
4. **PLANNING**:
    * Step-by-step planning for complex tasks.
    * Pseudocode required for critical logic.

## Fallback

If `AGENTS.md` is missing, ALERT THE USER immediately. Do not proceed with "default" behaviors.
