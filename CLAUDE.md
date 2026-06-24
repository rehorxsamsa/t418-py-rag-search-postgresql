# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Komunikovat s uživatelem vždy v češtině** (odpovědi, vysvětlení, shrnutí).

## What this is

A RAG demo (interview talking-point project): semantic document search backed by
PostgreSQL + `pgvector`, with optional Claude answer synthesis. FastAPI app, runs
entirely in Docker. The README is in Czech.

## Commands

```bash
# Start the full stack (db + api), seeds 5 example docs on first boot
docker compose up --build
# API: http://localhost:8000  ·  OpenAPI docs: http://localhost:8000/docs

# Tests — these hit the LIVE stack over HTTP, they are not isolated unit tests.
# The stack must already be running on localhost:8000.
pip install httpx pytest
pytest tests/
pytest tests/test_api.py::test_search_ranking   # single test
```

`cp .env.example .env` before first run; set `ANTHROPIC_API_KEY` only if you want
the `/api/ask` endpoint to generate answers (otherwise it degrades gracefully — see below).

## Architecture

Layered: **routers → services → database**, with cross-cutting config.

- `app/main.py` — FastAPI app + `lifespan`: calls `init_db()` and seeds `SEED_DOCS`
  only if the table is empty. Mounts the `documents` router under `/api`. Also exposes
  an unprefixed `/health` — it backs the Docker `HEALTHCHECK` and `test_health`.
- `app/routers/documents.py` — endpoints: `/api/documents` (CRUD), `/api/search`
  (pure vector search with similarity scores), `/api/ask` (RAG).
- `app/services/embeddings.py` — `EmbeddingProvider` ABC behind a factory
  `get_embedding_provider()` (`@lru_cache` singleton). Add cloud providers here;
  the rest of the app never imports a concrete provider.
- `app/services/rag.py` — the RAG loop: `retrieve()` (cosine-distance top-k) →
  Claude grounded answer. Uses model `claude-sonnet-4-6`.
- `app/database.py` — SQLAlchemy 2.0. `Document` model with a `Vector` column;
  `init_db()` creates tables + an IVFFlat cosine index. `get_session()` is a
  commit/rollback context manager.
- `app/config.py` — pydantic-settings `Settings`, single `settings` instance.

## Things that will bite you

- **Embedding dimension is wired in three places that must agree:** the local model
  `all-MiniLM-L6-v2` (384 dims), `settings.embedding_dim` (default 384), and the
  `Vector(settings.embedding_dim)` column. Swapping the model means changing the dim
  AND recreating the table/index (drop the `pgdata` volume).
- **No hot reload.** `docker-compose.yml` mounts `./app` read-only and uvicorn runs
  without `--reload`, so code changes require `docker compose restart api` (or rebuild).
- **`vector` extension** comes from `init.sql` (run once on a fresh `pgdata` volume).
  To reset DB state entirely: `docker compose down -v`.
- **Graceful degradation:** with no `ANTHROPIC_API_KEY`, `/api/ask` returns a stub
  answer + sources instead of calling Claude; `/api/search` is unaffected. Don't
  "fix" this by requiring the key.
- The local sentence-transformers model downloads on first use inside the container.
- **Only `EMBEDDING_PROVIDER=local` is actually implemented.** The config comment and
  the `embeddings.py` docstring mention Voyage/OpenAI, but `get_embedding_provider()`
  raises `ValueError` for any other value — those are extension points, not features.

## Workspace rule

This repo lives in a workspace whose `CLAUDE.md` forbids any `git push` / remote
operations. Local commits only; never push or create remotes without an explicit instruction.
