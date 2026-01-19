# RHEA NOIR Intelligence v2.0
```text
██████╗ ██╗  ██╗███████╗██████╗     ███╗   ██╗ ██████╗ ██╗██████╗ 
██╔══██╗██║  ██║██╔════╝██╔══██╗    ████╗  ██║██╔═══██╗██║██╔══██╗
██████╔╝███████║█████╗  ██████╔╝    ██╔██╗ ██║██║   ██║██║██████╔╝
██╔══██╗██╔══██║██╔══╝  ██╔══██╗    ██║╚██╗██║██║   ██║██║██╔══██╗
██║  ██║██║  ██║███████╗██║  ██║    ██║ ╚████║╚██████╔╝██║██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚═╝  ╚═╝
```
🌌 **Cybernetic Creative Partner & Web Intelligence Officer**

*Powered by Google Gemini 3 Pro (Thinking) and Vertex AI*

---

## 📡 API Reference (Server)
**Base URL**: `http://localhost:8081`
**Docs**: [http://localhost:8081/docs](http://localhost:8081/docs)

### Core Capabilities

#### `POST /cowrite`
**Co-Writer Engine**
Collaborates with the Worldbuilding Database (Notion).
```json
{
  "instruction": "Create a new faction based on Void tech.",
  "context": "Optional manual context override..."
}
```

#### `POST /generate-image`
**Visual Cortex (Imagen 3)**
Generates high-fidelity assets ("Nano Banana" pipeline).
```json
{
  "prompt": "Cinematic shot of a neon city, void aesthetic, 8k"
}
```

#### `POST /research`
**Deep Research (Gemini Grounding)**
Performs web research and synthesis.
```json
{
  "query": "Latest trends in immersive theater technology 2026"
}
```

### Protocol Compatibility (Kaedra/Fleet)

#### `POST /v1/chat/completions`
**A2A Interface**
Standard chat endpoint for Agent-to-Agent communication.
```json
{
  "messages": [{"role": "user", "content": "Hello Rhea, status?"}],
  "model": "gemini-3-flash"
}
```

#### `GET /v1/models`
**Discovery**
Lists available cortex models.

---

## 🛠️ CLI Tools

### 🎨 Nano Banana (Visual Engine)
```bash
# Generate a new Hero asset for the website
python utilities/rhea_asset_gen.py
```

### 📝 Notion Co-Writer (Standalone)
```bash
# Start a CLI co-writing session
python utilities/co_writer.py
```

---

## 📜 Deployment & Infrastructure

### 🌐 Web Presence
- **Omniverse Nights**: [Localhost:4444](http://localhost:4444)
- **Status**: 🟢 Online
- **Stack**: Next.js 16, React 19, Tailwind CSS (Vibe Coded)

### ☁️ Cloud Architecture
- **Project**: `rhea-noir` (GCP)
- **Region**: `us-central1`
- **Services**: Vertex AI, Cloud Run, Firebase

---

## 🚀 Quick Start

### 1. Environment Setup
Create `.env` with:
```env
GOOGLE_PROJECT_ID="rhea-noir"
NOTION_TOKEN="secret_..."
NOTION_WORLDBUILDING_DB_ID="2e5ca671..."
```

### 2. Launch Server
```bash
# Run the API server
python rhea_server.py
```

---

*Who Visions LLC © 2026*
