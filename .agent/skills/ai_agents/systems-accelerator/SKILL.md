---
name: systems-accelerator
description: A rigorous framework for building complex systems (compilers, engines, optimizers) using Agentic workflows. Enforces 'Golden File' testing and Deep Research context.
keywords: [rust, systems, compiler, optimizer, snapshot-testing, golden-file, deep-research]
priority: 90
---

# Systems Accelerator Protocol

> **Origin**: Derived from *'From Idea to Execution: Building a BigQuery SQL Optimizer with Antigravity'* by Marcelo Costa.

This skill transforms Antigravity from a simple code assistant into a **Systems Engineering Partner**. It is designed for complex, high-stakes domains (Rust, C++, Compilers, Distributed Systems) where correctness is paramount and boilerplate is heavy.

## 1. The Setup: Thinking Before Coding

**Rule**: Never start a complex system with an empty context.

1.  **Deep Research Injection**: Before writing code, use the `search_web` tool to build a "Dossier" on the problem domain.
    *   *Example*: "Search for open-source repositories using e-graphs for SQL optimization. Summarize architectural patterns."
2.  **Context Loading**: Feed this synthesized context into the session. The agent must "study" the state of the art before attempting implementation.

## 2. The "Golden File" Strategy (Agent Guardrails)

**Rule**: Agents can write valid code that is logically wrong. Unit tests are insufficient. **Snapshot Tests are mandatory.**

*   **Why**: If the agent refactors logic (e.g., an optimizer rule), traditional tests might verify *compilation*, but fail to catch subtle behavioral changes.
*   **Implementation**:
    *   **Rust**: Use `insta`.
    *   **JS/TS**: Use `jest` snapshots.
    *   **Python**: Use `pytest-snapshot` or `syrupy`.
*   **Workflow**:
    1.  Agent writes code.
    2.  Agent runs tests.
    3.  If snapshot fails, Agent *reads the diff* from stdout.
    4.  Agent self-corrects based on the diff.

## 3. The Artifact Lifecycle

Strict adherence to the 3-Artifact System is required to maintain architectural integrity.

### 3.1 The Blueprint (`implementation_plan.md`)
*   **Purpose**: The Technical Design Doc.
*   **Action**: You MUST propose the module structure (e.g., `src/parser.rs`, `src/cost.rs`) here.
*   **Review**: User reviews architectural decisions (e.g., "Use a Byte-based cost model, not Row-based") *before* code generation.

### 3.2 The Checklist (`task.md`)
*   **Purpose**: Dependency Management.
*   **Action**: Break down the Blueprint into atomic, ordered steps. Track progress in real-time.

### 3.3 The Proof (`walkthrough.md`)
*   **Purpose**: The "Receipt" of work.
*   **Action**: Document *exactly* how the system was verified.
    *   Include CLI commands used (`cargo run -- ...`).
    *   Include Snapshot diffs or Test outputs.
    *   *Optional*: For UI, include a Browser Recording using `open_browser`.

## 4. "Vibe Coding" Complex Logic

For complex logical components (e.g., rewriting rules, cost models), do not dictate implementation details. Dictate **Intent**.

*   *Bad Prompt*: "Write a function that iterates over the nodes and checks if..."
*   *Good Prompt (Vibe)*: "Create a rule that checks which columns are actually used in a SELECT statement and pushes that requirement down to the data source."

Let the agent architect the solution (e.g., patching the analysis module to track column usage) based on the high-level intent.
