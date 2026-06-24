# Semantic Document Search (RAG demo)

Sémantické vyhledávání v dokumentech postavené na **vektorové databázi** a **RAG** pipeline s Claude. Celé běží v Dockeru a nastartuje jedním příkazem. Součástí je i jednoduché **webové UI** na `http://localhost:8000/`.

## Co to ukazuje (talking points na pohovor)

- **RAG pipeline** — embedding dotazu → vektorové vyhledání nejbližších dokumentů → Claude odpoví *jen* z nalezeného kontextu (omezení halucinací).
- **Vektorová DB** — PostgreSQL + `pgvector`, cosine similarity, IVFFlat index. Žádný samostatný vektorový store.
- **Čistá architektura** — oddělené vrstvy: routery → služby (embeddings, RAG) → databáze. Provider embeddingů je za rozhraním, jde vyměnit (lokální model ↔ cloud) bez zásahu do zbytku.
- **Graceful degradation** — bez `ANTHROPIC_API_KEY` funguje jako čisté sémantické vyhledávání; klíč jen zapne generování odpovědí.
- **Production-ready detaily** — healthchecky, multi-stage závislosti, env config přes pydantic-settings, OpenAPI dokumentace zdarma, testy.

> Podrobný rozbor vrstev a designových rozhodnutí je v [ARCHITEKTURA.md](ARCHITEKTURA.md).

## Architektura

```
┌─────────┐   embed    ┌──────────────┐   retrieve   ┌──────────┐
│  Dotaz  │ ─────────▶ │  pgvector    │ ───────────▶ │  Claude  │
└─────────┘            │  (top-k)     │   + context  │  odpověď │
                       └──────────────┘              └──────────┘
```

## Spuštění

```bash
cp .env.example .env          # volitelně doplň ANTHROPIC_API_KEY
docker compose up --build
```

Při startu se naseeduje 5 ukázkových dokumentů. Pak je k dispozici:

- **Webové UI** — `http://localhost:8000/` (vyhledávání, dotaz na AI, správa dokumentů)
- **Interaktivní API dokumentace** — `http://localhost:8000/docs`

## Endpointy

| Metoda | Cesta | Popis |
|--------|-------|-------|
| `GET`  | `/` | Webové UI (jednostránková aplikace) |
| `POST` | `/api/documents` | Přidá a zaembedduje dokument |
| `GET`  | `/api/documents` | Seznam dokumentů (vč. obsahu) |
| `DELETE` | `/api/documents/{id}` | Smaže dokument |
| `GET`  | `/api/search?q=...` | Čisté sémantické vyhledávání se skóre |
| `POST` | `/api/ask` | RAG — vyhledá kontext a nechá Claude odpovědět |
| `GET`  | `/health` | Healthcheck |

## Příklady

```bash
# Sémantické vyhledávání
curl "http://localhost:8000/api/search?q=jak%20funguje%20izolace%20aplikaci&top_k=3"

# RAG odpověď (vyžaduje ANTHROPIC_API_KEY)
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Co je RAG a proč omezuje halucinace?", "top_k": 3}'
```

## Testy

```bash
# se spuštěným stackem
pip install httpx pytest
pytest tests/
```

## Tech stack

Python 3.12 · FastAPI · SQLAlchemy 2.0 · PostgreSQL 16 + pgvector · sentence-transformers · Anthropic SDK · Docker Compose
