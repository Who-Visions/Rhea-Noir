# RHEA NOIR Intelligence v3.1

```text
██████╗ ██╗  ██╗███████╗██████╗     ███╗   ██╗ ██████╗ ██╗██████╗ 
██╔══██╗██║  ██║██╔════╝██╔══██╗    ████╗  ██║██╔═══██╗██║██╔══██╗
██████╔╝███████║█████╗  ██████╔╝    ██╔██╗ ██║██║   ██║██║██████╔╝
██╔══██╗██╔══██║██╔══╝  ██╔══██╗    ██║╚██╗██║██║   ██║██║██╔══██╗
██║  ██║██║  ██║███████╗██║  ██║    ██║ ╚████║╚██████╔╝██║██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚═╝  ╚═╝
```

🌙 **Cybernetic Creative Partner & Web Intelligence Officer**

*Powered by Google Gemini 3 (Flash/Pro with Thinking) and Vertex AI*

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://python.org)
[![Pylint Score](https://img.shields.io/badge/Pylint-9.5%2B-brightgreen)](https://pylint.org)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

---

## 🔖 Release Notes (v3.1)

- Added architecture diagram and routing rules table
- Added memory semantics contract with `project_id` and `conversation_id` scoping
- Documented streaming support and endpoint capabilities
- Added security baseline (`X-API-Key`, isolation, prod secrets)
- Added error format and streaming contracts for SDK builders

---

## ✨ What is Rhea Noir?

Rhea Noir is an **AI-powered creative intelligence system** designed for worldbuilding, content generation, and web research. She serves as the creative backbone for the **Veil Verse** universe and powers the Who Visions LLC content pipeline.

### Core Capabilities

| Feature | Description |
|---------|-------------|
| 🧠 **Smart Routing** | Automatically routes queries to optimal Gemini models based on complexity |
| 🎨 **Visual Generation** | Creates high-fidelity images via Gemini 3 Pro Image ("Nano Banana" pipeline) |
| 📚 **Memory System** | Short-term and long-term memory with semantic search and cloud sync |
| 🔍 **Web Research** | Google-grounded search with real-time information synthesis |
| ✍️ **Co-Writing** | Collaborative worldbuilding with Notion database integration |
| 🎬 **YouTube Ingestion** | Transcript extraction and chunking for knowledge base building |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                  │
│              (CLI, Web, Kaedra, External Agents)                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RHEA BRIDGE SERVER                           │
│                    (FastAPI @ :8081)                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ /cowrite │  │/research │  │/generate │  │/v1/chat/...  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘   │
└───────┼─────────────┼─────────────┼───────────────┼────────────┘
        │             │             │               │
        ▼             ▼             ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     GEMINI 3 ROUTER                             │
│           (gemini3_router.py - Smart Model Selection)           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Signal              → Model                              │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ < 1k tokens, simple → Flash (minimal thinking)          │   │
│  │ Multi-step reason   → Pro (high thinking)               │   │
│  │ Image generation    → Pro Image                         │   │
│  │ Web grounding       → Flash/Pro + Google Search         │   │
│  │ Voice/TTS           → Gemini 2.5 Flash TTS              │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   MEMORY     │    │   SKILLS     │    │   EXTERNAL   │
│  ┌────────┐  │    │  ┌────────┐  │    │  ┌────────┐  │
│  │ Short  │  │    │  │ Stitch │  │    │  │ Notion │  │
│  │  Term  │  │    │  │ (Image)│  │    │  │   DB   │  │
│  ├────────┤  │    │  ├────────┤  │    │  ├────────┤  │
│  │ Long   │  │    │  │ yt-dlp │  │    │  │Firebase│  │
│  │  Term  │  │    │  │(Video) │  │    │  │ (Sync) │  │
│  └────────┘  │    │  └────────┘  │    │  └────────┘  │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## 🧠 Memory Semantics

| Layer | Scope | TTL | Trigger |
|-------|-------|-----|---------|
| **Short-term** | `conversation_id` | Auto-evict on conversation end | Every message |
| **Long-term** | `project_id` | Persistent | Explicit commit, ingestion jobs, cowrite completion |

**Session boundary**: `conversation_id` (unique per chat session)  
**Reads**: Semantic search, scoped by `project_id`  
**Writes**: Tagged, embedded, deduplicated  
**Sync**: Firebase Firestore (optional cloud backup)

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/Who-Visions/Rhea-Noir.git
cd Rhea-Noir
pip install -r requirements.txt
```

### 2. Environment Setup
Create `.env` with:
```env
GEMINI_API_KEY="your-gemini-api-key"
GOOGLE_PROJECT_ID="rhea-noir"
NOTION_TOKEN="secret_..."
NOTION_WORLDBUILDING_DB_ID="2e5ca671..."
```

### 3. Launch Server
```bash
python rhea_bridge_server.py
```

**API Docs**: [http://localhost:8081/docs](http://localhost:8081/docs)

---

## 📡 API Reference

**Production**: `https://rhea-noir-145241643240.us-central1.run.app`  
**Local**: `http://localhost:8081`  
**Interactive Docs**: `/docs` (Swagger UI)

### System & Discovery

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root status |
| `/health` | GET | Health check |
| `/health/detailed` | GET | Detailed health with dependencies |
| `/config` | GET | Current configuration |
| `/v1` | GET | V1 API root |
| `/v1/api` | GET | V1 API info |
| `/v1/models` | GET | List available models |

### Agent-to-Agent (A2A)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/a2a` | GET | Get A2A agent card |
| `/a2a/card` | GET | A2A card alias |
| `/agent-card` | GET | Agent card alias |
| `/.well-known/agent.json` | GET | Standard agent discovery |
| `/v1/chat/completions` | POST | OpenAI-compatible chat |
| `/v1/chat` | POST | Chat (legacy) |

### Generation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | Fleet generate (text) |
| `/generate-image` | POST | Image generation (Nano Banana) |
| `/generate/video` | POST | Video generation |
| `/generate/world` | POST | World generation |
| `/v1/embeddings` | POST | Create embeddings |

### Research & Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/research` | POST | Start research task |
| `/research/{task_id}` | GET | Get research status |
| `/search` | POST | Fleet search |
| `/analyze-url` | POST | Analyze URL content |
| `/execute-code` | POST | Execute code |

### Lore & Worldbuilding

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cowrite` | POST | Collaborative worldbuilding |
| `/lore/feed` | GET | Get lore feed |
| `/lore/weighted` | GET | Get weighted lore |
| `/lore/bible` | GET | Get world bible |
| `/lore/search` | GET | Search lore |
| `/lore/{id}` | GET | Get lore item |
| `/worlds` | GET | List worlds |

### Story Engine

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/story/sessions` | GET | List story sessions |
| `/story/session` | POST | Create story session |
| `/story/session/{session_id}` | GET | Get story session |
| `/story/generate` | POST | Generate story content |

### Sync & Ingestion

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/ingest` | POST | Ingest content |
| `/sync` | POST | Manual sync |
| `/sync/{world_id}` | GET | Sync status |
| `/webhook/notion` | POST | Notion webhook |

### Smart Home (Lights/Razer)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/lights/status` | GET | Get lights status |
| `/lights/set` | POST | Set light state |
| `/lights/effect` | POST | Run light effect |
| `/lights/presets` | GET | Get light presets |
| `/lights/preset/{preset_id}` | POST | Apply light preset |
| `/razer/status` | GET | Get Razer status |
| `/razer/effect` | POST | Set Razer effect |
| `/razer/sync` | POST | Sync Razer |

### Webhooks & Integrations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/hooks/slack/events` | POST | Slack events |
| `/hooks/slack/commands` | POST | Slack commands |
| `/hooks/pubsub` | POST | Pub/Sub webhook |

### Validation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/validate` | GET | Run full validation |
| `/validate/quick` | GET | Quick validation |

---

### `/v1/chat/completions` Capabilities

| Feature | Status |
|---------|--------|
| Roles: `system`, `user`, `assistant` | ✅ Supported |
| Streaming (`stream=true`) | ✅ Supported |
| Function/Tool Calling | 🗺️ Roadmap |
| Project Scoping (`project_id`) | ✅ Supported |

### Error Format

All errors return:
```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests",
    "request_id": "req_...",
    "retry_after_s": 10
  }
}
```

| Code | Description |
|------|-------------|
| `INVALID_REQUEST` | Malformed request body |
| `UNAUTHORIZED` | Missing or invalid API key |
| `FORBIDDEN` | Valid key, insufficient permissions |
| `NOT_FOUND` | Resource does not exist |
| `RATE_LIMITED` | Too many requests |
| `INTERNAL` | Server error |

> **Note**: `request_id` is generated server-side and returned in the `X-Request-ID` response header.

### Streaming

`/v1/chat/completions` supports Server-Sent Events when `stream=true`.

| Event | Description |
|-------|-------------|
| `message.delta` | Partial response chunk |
| `message.completed` | Final response, stream ends |
| `error` | Error occurred, stream ends |

### Request Examples

#### `POST /cowrite`
```json
{
  "instruction": "Create a new faction based on Void tech.",
  "context": "Optional manual context override...",
  "project_id": "veilverse-core"
}
```

#### `POST /generate-image`
```json
{
  "prompt": "Cinematic shot of a neon city, void aesthetic, 8k"
}
```

#### `POST /research`
```json
{
  "query": "Latest trends in immersive theater technology 2026"
}
```

#### `POST /v1/chat/completions`
```json
{
  "messages": [{"role": "user", "content": "Hello Rhea, status?"}],
  "model": "gemini-3-flash",
  "project_id": "veilverse-core",
  "stream": false
}
```

---

## 🔐 Security & Auth

| Layer | Implementation |
|-------|----------------|
| **API Auth** | `X-API-Key` header (environment-configured) |
| **Environment Separation** | `.env` for dev, Cloud Run secrets for prod |
| **Network** | Internal-only by default; allowlist for external |
| **Data Isolation** | `project_id` scoping prevents memory bleed |

**Enforcement**:
- Requests missing `X-API-Key` are rejected with `401 UNAUTHORIZED`
- Logs contain only `request_id`; raw prompts are never logged unless `DEBUG_MODE=true`

> ⚠️ **Note**: Rhea Noir is currently designed for internal/trusted workloads. For external-facing deployments, add Firebase Auth or OAuth.

---

## 📁 Project Structure

```
Rhea-Noir-Ai/
├── rhea_noir/              # Core intelligence package
│   ├── gemini3_router.py   # Smart model routing (Flash/Pro)
│   ├── memory/             # Short-term & long-term memory
│   ├── skills/             # Modular skill system (stitch, ytdlp, etc.)
│   └── harness.py          # Task management harness
├── scripts/
│   ├── ingestion/          # Data pipeline scripts
│   ├── visuals/            # Asset generation scripts
│   └── diagnostics/        # Health & monitoring tools
├── rhea_bridge_server.py   # FastAPI server
└── requirements.txt
```

---

## 🧪 Code Quality

All code passes static analysis with **Pylint scores ≥ 9.5/10**:

| Package | Score |
|---------|-------|
| `rhea_noir` | 9.57 |
| `scripts/ingestion` | 9.68 |
| `scripts/visuals` | 9.66 |
| `scripts/diagnostics` | 9.68 |

```bash
# Verify yourself
pylint rhea_noir
python -m compileall rhea_noir -q
```

---

## 🛠️ CLI Tools

### Interactive Chat
```bash
python rhea_noir_cli.py
```

### Asset Generation (Nano Banana)
```bash
python scripts/visuals/generate_omniverse_assets.py
```

### YouTube Ingestion
```bash
python scripts/ingestion/ingest_youtube.py --url "https://youtube.com/watch?v=..."
```

---

## ☁️ Infrastructure

| Component | Technology |
|-----------|-----------|
| **AI Models** | Gemini 3 Flash/Pro (Thinking), Gemini 2.5 Flash TTS |
| **Cloud** | GCP (Vertex AI, Cloud Run, Firebase) |
| **Database** | Notion (Worldbuilding), Firebase (Memory Sync) |
| **Server** | FastAPI with Uvicorn |

> **Version Note**: Gemini model aliases (e.g., `gemini-3-flash`) may resolve to newer revisions. Pin explicit versions in production if determinism is required.

---

## 🗺️ Roadmap

**Priority Order**: OpenAPI hardening → tool calling → SDK → Vertex spec → skills registry

- [ ] OpenAPI schema hardening
- [ ] Agent-to-Agent tool calling
- [ ] Rhea Noir Python SDK
- [ ] Vertex AI deployment spec
- [ ] Skill Registry endpoint (`/v1/skills`)
- [ ] Health check endpoint (`/healthz`)

---

## 🔗 Links

- **Instagram**: [@aiwithdav3](https://instagram.com/aiwithdav3)
- **YouTube**: [Ai with Dav3](https://youtube.com/aiwithdav3)
- **Website**: [WhoVisions.com](https://whovisions.com)

---

*Who Visions LLC © 2026*
