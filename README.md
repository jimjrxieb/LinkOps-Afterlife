# LinkOps Afterlife (OSS Demo)

Create a speaking avatar + memory-backed chat using a **local** LLM and **RAG**.
- Default: fully local (no paid APIs).
- Optional: bring your own keys (ElevenLabs, D‑ID, OpenAI) — wired in Sprint 2.

## Quickstart (local)
```bash
docker compose up --build -d
docker compose exec api python preprocess.py   # seed sample data
open http://localhost:5173
```

## Stack

* **API:** FastAPI (LLM: Qwen2.5-1.5B, RAG: Chroma)
* **UI:** Vite + React
* **Engines:** modular (`/api/engines`) with toggles