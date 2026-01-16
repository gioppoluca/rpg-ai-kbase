# OpenWebUI RAG Gateway (FastAPI + Memvid + Ollama)

This project exposes an **OpenAI-compatible** API (`/v1/models`, `/v1/chat/completions`) so **Open WebUI** can talk to it as a model provider, while the backend does **RAG** using:

- **Memvid** as the on-disk “memory” (single `.mv2` file)
- **Ollama** as the local LLM
- A simple **ingestion API** to chunk and ingest Markdown + PDFs into Memvid

## Folder layout

```
openwebui-rag-fastapi/
  app/                # FastAPI code
  data/md/            # your Markdown vault (input)
  data/pdf/           # your PDFs (input)
  memvid_store/       # output .mv2 files
```

## Quick start

```bash

docker run --rm -it -p 8000:8000 -v ${PWD}:/app -w /app -e MEMVID_DIR=/app/memvid -e MEMVID_INDEX=/app/memvid/kb.mv2 --env-file .env   python:3.12-slim /bin/bash
docker run --rm -it -p 8000:8000 -v ${PWD}:/app -w /app -e MEMVID_DIR=/app/memvid -e MEMVID_INDEX=/app/memvid/kb.mv2 --env-file .env   python:3.12-slim /bin/bash

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/api/health
```

## Ingest (chunk + store into Memvid)

- Markdown:

```bash
curl -X POST http://localhost:8000/api/ingest/md
```

- PDFs:

```bash
curl -X POST http://localhost:8000/api/ingest/pdf
```

- Both:

```bash
curl -X POST http://localhost:8000/api/ingest/all
```

## Configure Open WebUI to use this server

Open WebUI supports connecting to **OpenAI-compatible** servers from **Admin Settings → Connections → OpenAI**. Use the **API URL** that points to this service.

Example:
- API URL: `http://<your-host>:8000/v1`
- API Key: leave blank unless you set `API_KEY` in `.env`

(These steps follow Open WebUI’s “OpenAI-compatible servers” connection flow.)

## What endpoints are implemented

### OpenAI-compatible

- `GET /v1/models` (exposes a single model id `local-rag`)
- `POST /v1/chat/completions` (runs RAG: retrieve from Memvid, answer with Ollama)

### Ingestion & debug

- `POST /api/ingest/md`
- `POST /api/ingest/pdf`
- `POST /api/ingest/all`
- `POST /api/search` (debug memvid search)
- `GET /api/config`
- `GET /api/health`

## Notes about Memvid

Memvid provides a Python SDK (`memvid-sdk`) with `create()` / `use()` and `put()` / `find()` primitives. This project uses that SDK so we can ingest chunks and run retrieval locally from a single `.mv2` file.

## Next steps (we’ll implement next)

- Better PDF parsing for RPG manuals (layout aware) and optional Docling pipeline
- A proper embeddings strategy (either Ollama embeddings or Memvid’s own vector feature)
- Source-aware response formatting (clear citations like `Book.pdf p.142` / `file.md > H2`)
