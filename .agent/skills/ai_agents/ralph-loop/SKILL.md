---
name: ralph-loop
description: A verified iteration loop pattern where external tools (Docker, Compilers, Tests) decide when to stop, not the LLM. "It's better to fail predictably than succeed unpredictably."
keywords: [adk, google-adk, loop, verification, docker, testing, reliability]
priority: 90
---

# Ralph Loop Protocol

> **Origin**: Derived from *'Ralph Loop with Google ADK: AI Agents That Verify, Not Guess'* by Thomas Chong.

The Ralph Loop philosophy is simple: **Don't trust the AI to judge its own work.** Standard loops often fail because the model that wrote the code also evaluates it. Ralph Loop enforces success through objective, external systems.

# Ralph Loop Protocol

> **Origin**: Derived from *'Ralph Loop with Google ADK'* by Thomas Chong, *'Ralph Claude Code'* by Frank Bria, and *'Ralph Orchestrator'* by Mikey O'Brien.

The Ralph Loop philosophy is simple: **Don't trust the AI to judge its own work.** Standard loops often fail because the model that wrote the code also evaluates it. Ralph Loop enforces success through objective, external systems.

## 1. The Core Principle

**Rule**: The exit condition of a loop MUST be driven by a deterministic tool, never by an LLM's sentiment.

*   ❌ **Bad**: "Review the code. If it looks good, call exit_loop()."
*   ✅ **Ralph**: "Check `state['build_verified']`. If True, call exit_loop()."

## 2. Implementation Paths

Choose the path that fits your stack.

### Path A: The Shell Loop (Lite/Portable)
*Based on `frankbria/ralph-claude-code`.*
Best for: Quick CI/CD scripts, local dev loops, shell-heavy environments.

1.  **Copy Resource**: `resources/ralph-lite.sh` to your project root.
2.  **Configure**: Edit the verification step in the script (lines 30-40) to run your specific tests (`npm test`, `cargo build`, etc.).
3.  **Run**: `./ralph-lite.sh "Implement feature X"`

**Key Feature**: "Dual Exit" Gate.
The loop only exits if **BOTH** conditions are met:
1.  The Agent *thinks* it is done.
2.  The External System *confirms* it passes.

### Path B: The Rust Orchestrator (Event-Driven)
*Based on `mikeyobrien/ralph-orchestrator`.*
Best for: Complex multi-agent systems, "Hats" (Personas), High-performance needs.

1.  **Install**: `npm install -g @ralph-orchestrator/ralph-cli` (or via cargo).
2.  **Configure**: Use `resources/rust-config.toml` as your `ralph.toml`.
3.  **Define Hats**:
    *   **Planner**: Breaks down work (`task.start` -> `plan.ready`).
    *   **Builder**: Writes code (`plan.ready` -> `build.done`).
    *   **Verifier**: Runs tests (`build.done` -> `test.passed` / `test.failed`).

**Key Feature**: Backpressure.
The Verifier "Hat" acts as a quality gate. It rejects `build.done` events if the build fails, sending a `test.failed` event back to the Builder with the error logs.

## 3. Architecture Pattern

Regardless of the implementation, the pattern remains:

1.  **Generator/Builder** (One-Shot): Makes the initial attempt. Fails fast.
2.  **Verifier** (Deterministic): Runs the external check. Updates state.
3.  **Refiner** (Iterative): Looks at the *error output* from the Verifier, explains the fix ("🔧 Fixing..."), and tries again.

## 4. When to Use

| ✅ Use Ralph Loop | ❌ Don't Use |
| :--- | :--- |
| **Objective Success**: `docker build`, `pytest`, `npm build` | **Subjective Quality**: "Is this funny?", "Is this pretty?" |
| **Binary Pass/Fail**: It works or it doesn't. | **Nuanced Tradeoffs**: Complexity vs Performance. |
| **Mechanical Tasks**: Config generation, refactoring, typing. | **Creative Tasks**: Story writing, brainstorming. |

