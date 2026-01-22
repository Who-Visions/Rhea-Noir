# Rhea Noir - Master Navigation Guide 🌙

## Project Intelligence
- **Project Name**: Rhea-Noir
- **Project Number**: 145241643240
- **Project ID**: `rhea-noir`
- **Billing Account ID**: `017C96-9F5010-A0338A`

## 📂 Codebase Structure

### 🧠 Core & Source
- **`rhea_noir/`**: The core python package containing the Rhea Noir agent logic, skills, and branding.
  - **`skills/`**: Agent capabilities (computer use, audio, etc.).
  - **`vertex/`**: Vertex AI integration logic.
  - **`PLAYBOOK.md`**: The Agent Protocol and harnessed loops.

### 📜 Scripts & Automation
- **`scripts/ingestion/`**: Bulk data ingestion scripts (`bulk_ingest_*.py`, `ingest_*.py`).
- **`scripts/manual_ingestion/`**: Manual/Specific ingestion routines (`manual_ingest_*.py`).
- **`scripts/diagnostics/`**: Debugging, auditing, and inspection tools (`debug_*.py`, `audit_*.py`, `check_*.py`).
- **`scripts/visuals/`**: Image generation and rendering scripts (`rhea_canonical_render.py` etc.).
- **`scripts/maintenance/`**: Database cleanup, backfills, and dumps (`backfill_*.py`, `merge_duplicates.py`).
- **`scripts/utils/`**: General purpose utilities.

### 📚 Documentation
- **`docs/`**: Project documentation, audit reports, and plans.
  - **`docs/MASTER_NAVIGATION.md`**: This file.

### 🗄️ Data
- **`data/transcripts/`**: Raw transcript files.
- **`data/logs/`**: Execution and audit logs.
- **`data/exports/`**: Database dumps and export files.

### 🌐 Web & API
- **`web/`**: Web interface components (if any).
- **`rhea_server.py`**: Main API server entry point.

## 🚀 Quick Start
1.  **Environment**: Ensure `.env` is configured with GCP credentials.
2.  **Install**: `pip install -r requirements.txt`
3.  **Run Server**: `python rhea_server.py`
4.  **Run CLI**: `python rhea_cli.py` (located in root or `rhea_noir/`).

## 🏃 Running Distributed Scripts
Because scripts are now located in subdirectories, you must run them as modules to ensure they can find the `rhea_noir` package and other dependencies.

**Correct Usage:**
```bash
# Run from the project root
python -m scripts.ingestion.ingest_batch_2
python -m scripts.diagnostics.debug_structure
python -m scripts.visuals.rhea_canonical_render
```

**Incorrect Usage:**
```bash
# Do NOT run directly by path (imports may fail)
python scripts/ingestion/ingest_batch_2.py
```

## 🔗 Key Services
- **Vertex AI**: See `rhea_noir/vertex/`
- **LoreDB**: See `services/` or `rhea_noir/services/`
- **BigQuery**: Syncs via `rhea_noir/sync/` (check `PLAYBOOK.md` for details).

---
*Maintained by Rhea Noir 🌙*
