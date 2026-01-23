---
name: blast-framework
description: A 5-step systematic framework (Blueprint, Links, Architect, Stylize, Trigger) for building robust AI agents and automations.
---

# BLAST Framework Skill

Use this framework when the user wants to build a complete "System" or "Automation" from scratch.

## The 5 Steps

### 1. **B**lueprint (Vision & Logic)
-   **Goal**: Define the "North Star" (Purpose).
-   **Source of Truth**: Where does data live? (e.g., Notion, Database).
-   **Inputs/Outputs**: What triggers it? What is the deliverable?

### 2. **L**inks (Connections)
-   **Integrations**: Identify necessary MCP (Model Context Protocol) servers or APIs.
-   **Credentials**: Ensure API keys and environment variables are set.
-   **Verification**: Test connections before proceeding (Virtual Handshake).

### 3. **A**rchitect (Structure)
-   **3-Layer Architecture**:
    1.  **Directives**: Markdown SOPs (Standard Operating Procedures) defining *what* to do.
    2.  **Orchestration**: The Agent logic that routes data.
    3.  **Execution**: Python/Node.js scripts that perform the actual work.
-   **Determinism**: Business logic must be reproducible.

### 4. **S**tylize (UI/UX & Payload)
-   **User Experience**: Ensure the output (Dashboard, Email, Notification) is formatted beautifully.
-   **Refinement**: Use "Breathtaking UI" principles. "Don't make the user think."

### 5. **T**rigger (Deployment)
-   **Automation**: Set up cron jobs or triggers (e.g., using Modal, GitHub Actions, or local schedulers).
-   **Hands-off**: The system should run without user intervention.
