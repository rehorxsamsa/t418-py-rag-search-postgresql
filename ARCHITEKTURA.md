# Architektura projektu

RAG demo (sémantické vyhledávání v dokumentech): FastAPI aplikace nad
PostgreSQL + `pgvector`, volitelně s Claude pro syntézu odpovědí. Celý stack
běží v Dockeru.

## Přehled

Architektura je **vrstvená: routery → services → database**, s průřezovou
konfigurací. Každá vrstva má jasnou odpovědnost a závisí jen na vrstvě pod sebou.

```
HTTP požadavek
     │
     ▼
app/main.py                    ← kompozice aplikace (FastAPI + lifespan)
     │  mountuje router pod /api, seeduje data při startu
     ▼
app/routers/documents.py       ← HTTP vrstva (endpointy, validace přes schemas)
     │
     ├──→ app/services/embeddings.py   text → vektor (singleton provider)
     ├──→ app/services/rag.py          retrieve top-k + Claude odpověď
     │
     ▼
app/database.py                ← perzistence (SQLAlchemy 2.0 + pgvector)
     │
     ▼
PostgreSQL + pgvector          ← Docker služba `db` (image pgvector/pgvector:pg16)
```

Průřezově: `app/config.py` (konfigurace z env) a `app/schemas.py` (Pydantic
modely pro vstup/výstup) používá více vrstev.

## Vrstvy

### 1. `app/main.py` — kompozice aplikace

- Vytváří instanci FastAPI (`title`, `description`, `version`).
- Přes `lifespan` (asynchronní context manager) při startu:
  1. zavolá `init_db()` (vytvoří tabulky + index),
  2. **naseeduje 5 ukázkových dokumentů (`SEED_DOCS`), ale jen pokud je tabulka
     prázdná** — opakovaný start data neduplikuje.
- Mountuje router `documents` pod prefix `/api`.
- Vystavuje neprefixovaný `GET /health` — pohání Docker `HEALTHCHECK`
  (viz `Dockerfile`) i `test_health`.

### 2. `app/routers/documents.py` — HTTP vrstva

Definuje endpointy a řeší jen vstup/výstup, ne business logiku:

| Endpoint | Metoda | Popis |
|---|---|---|
| `/api/documents` | `POST` | Embedne a uloží dokument (status 201) |
| `/api/documents` | `GET` | Vrátí seznam dokumentů |
| `/api/documents/{id}` | `DELETE` | Smaže dokument (404 pokud neexistuje) |
| `/api/search` | `GET` | **Čisté vektorové vyhledávání** se skóre podobnosti |
| `/api/ask` | `POST` | **RAG**: vyhledání + Claude generuje odpověď |

`/api/search` je oddělené od `/api/ask` záměrně: vyhledávání nikdy nevolá LLM,
RAG ano. Vzdálenost se ve výsledcích převádí na skóre `round(1 - distance, 4)`.

### 3. `app/services/` — business logika (jádro projektu)

**`embeddings.py` — generování embeddingů**
- `EmbeddingProvider` je abstraktní třída (ABC) s metodou `embed(texts) -> vektory`.
- `LocalEmbeddingProvider` běží `all-MiniLM-L6-v2` lokálně (384 dim,
  `normalize_embeddings=True`), bez externích volání ani API klíče.
- Továrna `get_embedding_provider()` je `@lru_cache(maxsize=1)` **singleton** —
  model se načte jednou.
- **Klíčový vzor:** zbytek aplikace nikdy neimportuje konkrétního providera, jen
  tuto abstrakci. Nový cloudový provider se přidá jen zde.

**`rag.py` — Retrieval-Augmented Generation**
- `retrieve(query, top_k)` — embedne dotaz a vrátí top-k dokumentů podle
  kosinové vzdálenosti.
- `answer(query, top_k)` — celá RAG smyčka: retrieve → poskládání kontextu →
  Claude (`claude-sonnet-4-6`) s `system` instrukcí odpovídat **striktně
  z kontextu** a citovat zdroje přes `[id]`. Vrací odpověď i seznam zdrojů.

### 4. `app/database.py` — perzistence

- SQLAlchemy 2.0. Model `Document` (`id`, `title`, `content`, `embedding`),
  kde `embedding` je sloupec `Vector(settings.embedding_dim)` z pgvector.
- `init_db()` vytvoří tabulky a **IVFFlat cosine index** pro vektorové dotazy.
- `get_session()` je context manager s automatickým commit/rollback.

### 5. `app/config.py` — konfigurace

pydantic-settings `Settings` s jedinou instancí `settings`, načtenou z env
proměnných / `.env`. Klíčové hodnoty: `database_url`, `anthropic_api_key`,
`embedding_provider`, `embedding_dim`.

### `app/schemas.py` — kontrakty API

Pydantic modely oddělené od databázových modelů: `DocumentIn`/`DocumentOut`,
`SearchResult`/`SearchResponse`, `AskRequest`/`AskResponse`. Drží HTTP vrstvu
nezávislou na perzistenci.

## Klíčová designová rozhodnutí

**Sémantické vyhledávání jako SQL dotaz.** Embeddingy nejdou do separátní
vektorové DB — pgvector přidá vektorový typ přímo do Postgresu, takže „najdi
nejpodobnější" je obyčejný dotaz s `ORDER BY` podle kosinové vzdálenosti a
`LIMIT top_k`.

**Graceful degradation.** Bez `ANTHROPIC_API_KEY` se `/api/ask` nerozbije —
vrátí stub odpověď + zdroje, takže aplikace dál funguje jako sémantické
vyhledávání. `/api/search` na klíči vůbec nezávisí. **Je to záměr, ne bug.**

**Vyměnitelný embedding provider.** Abstrakce + továrna umožňují přidat cloudové
providery, aniž by se zbytek aplikace dotkl.

## Pozor — implementační provázanosti

- **Embedding dimenze (384) musí souhlasit na třech místech:** lokální model
  `all-MiniLM-L6-v2`, `settings.embedding_dim` a sloupec
  `Vector(settings.embedding_dim)`. Výměna modelu znamená změnit dimenzi *a*
  znovu vytvořit tabulku/index (smazat volume `pgdata`).
- **Pouze `EMBEDDING_PROVIDER=local` je implementovaný.** Komentáře zmiňují
  Voyage/OpenAI, ale `get_embedding_provider()` pro jinou hodnotu vyhodí
  `ValueError` — jsou to rozšiřovací body, ne hotové funkce.
- **`vector` extension** vzniká z `init.sql` (spustí se jednou na čerstvém
  volume `pgdata`). Úplný reset DB: `docker compose down -v`.
- **Bez hot reloadu.** `docker-compose.yml` mountuje `./app` jako read-only a
  uvicorn běží bez `--reload`; změny kódu vyžadují `docker compose restart api`.

## Infrastruktura (Docker)

- **`db`** — image `pgvector/pgvector:pg16`, perzistence ve volume `pgdata`,
  `init.sql` mountovaný do init složky, healthcheck přes `pg_isready`.
- **`api`** — buildí se z `Dockerfile` (Python 3.12-slim, uvicorn na portu
  8000), startuje až po `service_healthy` databáze.

Spuštění: `docker compose up --build` → API na `http://localhost:8000`,
OpenAPI docs na `/docs`.
