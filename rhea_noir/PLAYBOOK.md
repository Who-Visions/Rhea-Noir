# RHEA NOIR HARNESS PLAYBOOK

## 🌙 The Autonomous Elegant Agent Protocol

This Playbook defines the strict "Rules of Engagement" for Rhea Noir's Persistent Agent Harness. Inspired by anthropic's long-running autonomous agent patterns, refined for elegant execution.

---

### 🏛️ Roles

#### 1. **Initializer Agent**
*   **Trigger**: Run once at the start of a new project epoch.
*   **Responsibility**:
    *   Create `task_list.json` (The PRD / backlog)
    *   Create `rhea_progress.json` (The Session Memory)
    *   Initialize `git` repo (if not exists)
    *   Sync initial state to BigQuery
    *   Does NOT write feature code

#### 2. **Coding Agent** (Recurring Loop)
*   **Trigger**: Run repeatedly until `task_list.json` is clear.
*   **The Elegant Loop**:

```
┌─────────────────────────────────────────────────┐
│  1. PRIME   │ Read rhea_progress.json,          │
│             │ task_list.json, git log           │
├─────────────────────────────────────────────────┤
│  2. SCOPE   │ Select ONE task (passed: false)   │
├─────────────────────────────────────────────────┤
│  3. ROUTE   │ Select model tier:                │
│             │ flash-lite → flash → pro → elite  │
├─────────────────────────────────────────────────┤
│  4. IMPLEMENT │ Write code, tests, config       │
├─────────────────────────────────────────────────┤
│  5. VERIFY  │ Run pytest for specific test      │
├─────────────────────────────────────────────────┤
│  6. DECIDE  │ Tests PASS → mark passed: true    │
│             │ Tests FAIL → log error, retry     │
├─────────────────────────────────────────────────┤
│  7. EVOLVE  │ Update keyword weights, learn     │
├─────────────────────────────────────────────────┤
│  8. COMMIT  │ Write to rhea_progress.json       │
│             │ Git commit, async BigQuery sync   │
└─────────────────────────────────────────────────┘
```

---

### 📜 Core Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| `task_list.json` | `~/.rhea_noir/harness/` | Source of Truth - what to build |
| `rhea_progress.json` | `~/.rhea_noir/harness/` | Session Memory - what was done |
| `evolution.json` | `~/.rhea_noir/harness/` | Learning state - preferences, weights |
| `tests/` | Project root | Adjudicator of Truth |

---

### 🧠 Model Routing Rules

```python
def select_model(task_complexity: str) -> str:
    """Route to appropriate model tier"""
    routing = {
        "simple": "gemini-2.5-flash-lite",   # Quick queries, classification
        "standard": "gemini-2.5-flash",       # Default conversations
        "complex": "gemini-2.5-pro",          # Reasoning, architecture
        "elite": "gemini-3-pro-preview",      # Research, advanced (global endpoint)
        "image": "gemini-2.5-flash-image",    # Multimodal tasks
    }
    return routing.get(task_complexity, "gemini-2.5-flash")
```

---

### ⚡ Async Persistence Layer

```
SQLite (Local) ──────► BigQuery (Cloud)
     │                      │
     │   60s lazy sync      │
     ▼                      ▼
Fast writes            Persistent memory
No blocking            Cross-device sync
```

---

### ⚠️ Golden Rules

1. **Trust Tests Only**
   Never mark a task as passed unless a verify command exits with code 0.

2. **One Token At A Time**
   Do not try to implement Year 1 and Year 4 in one session.

3. **Log Everything**
   The next agent has *zero* memory except what is written to `rhea_progress.json`.

4. **Async Persistence**
   Data sync to BigQuery happens in background; never block the main loop.

5. **Route Intelligently**
   Use flash-lite for simple work, escalate to pro/elite only when needed.

6. **Evolve Continuously**
   Track success/failure, update keyword weights, learn user preferences.

---

### 🚀 Long-Running Task Commands

| Command | Action |
|---------|--------|
| `/task <description>` | Start a long-running task |
| `/tasks` | List all running tasks |
| `/task-status <id>` | Check specific task status |
| `/task-cancel <id>` | Cancel a running task |

---

### 📊 Evolution Metrics

Rhea tracks and learns from:
- **Keyword importance** - Which topics matter most
- **Response preferences** - Length, detail, code style
- **Success rate** - What approaches work
- **Time patterns** - Activity rhythms

---

*Created by: Antigravity*
*Maintained by: Rhea Noir* 🌙
